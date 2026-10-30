#!/usr/bin/env python3
"""
nbt_container.py -- parser/extractor for the Harman/Becker "WOODOO / IOC-BOLO"
scripted-flash container used by BMW NBT Evo (HU_NBT2) firmware images.

These are the <class>_<sgbm>.bin.007_051_002 files (class = btld | swfl | ibad)
from your own PSdZData software pool (see docs/psdzdata-manifest.md).  The container is a flat, byte-packed stream of
records with NO alignment/padding.  Every record (including the 10-byte leading
"file header") follows ONE uniform 9-byte grammar:

  byte0      marker / record type (uint8)
               0x01 = stream-start / file-header record (degenerate: 1-byte body)
               0x02 = descriptor / script record -- body is ASCII "Key=Val;..."
               0x03 = data record (DRIVE/DVD-class binary payload)
               0x04 = data record (NOR/IOC/FIL binary payload)
             Rule: marker 0x02 => ASCII metadata body; ANY OTHER marker => binary
             payload body.  (We never assume a fixed set of data markers; we only
             special-case 0x02 as "this body is metadata".)
  byte1..2   16-bit LITTLE-ENDIAN group index.  A descriptor (0x02) and all of
             its following data records share one index; the index increments
             per logical group and wraps cleanly from 0x00FF -> 0x0100 via byte2.
  byte3..6   32-bit LITTLE-ENDIAN body length.  This is the ASCII metadata length
             for 0x02 records and the binary payload length for data records.
  byte7      segment field.  On a descriptor = count of data records that belong
             to this group (0 => pure script record, no data).  On a data record
             = the segment ordinal (1..N) within the group.  (Informational only;
             the parser does NOT rely on it for chaining -- it relies purely on
             header lengths walking to EOF.)
  byte8      flags / reserved -- always 0x00 across every file examined.

The 9-byte header is immediately followed by <length> bytes of body; the next
record header begins right after.  record_end = record_start + 9 + length.
Records chain to EXACT EOF (leftover bytes == 0) on a well-formed file.

A logical PAYLOAD is the concatenation of all consecutive data records (markers
!= 0x02) that follow a descriptor before the next descriptor.  Multi-segment
files (e.g. ibad mp4 animations with Append=On) split into several data records
sharing one index; we concatenate them in stream order.

The final group of every file resets the index to 0x0002 and is the BMW SWE
RSA-1024/MD5 flash *signature* block (descriptor Name=F0002000.nsw;Tag=FIL +
a 512-byte data record ending "File intentionally 512 Bytes long").  This is the
flash signature, NOT NOR/flash content, but it is a perfectly normal record and
is parsed/extracted like any other.

Stdlib only.  Streams the file (seek + bounded reads); never loads a whole
multi-hundred-MB / GB image into memory.

CLI:
  nbt_container.py list    <image.bin>
  nbt_container.py extract <image.bin> <outdir>
"""

import sys
import os
import re
import hashlib
import argparse

HEADER_LEN = 9
MARKER_DESCRIPTOR = 0x02  # body is ASCII metadata
# Any other marker (0x01, 0x03, 0x04, ...) => body is binary payload.

# Read chunk size for streaming copy / hashing.
_COPY_CHUNK = 1 << 20  # 1 MiB

# Cap on how many metadata bytes we will read into memory for a descriptor.
# Real descriptors are well under 1 KiB; guard against a corrupt huge length.
_MAX_META_INMEM = 1 << 20  # 1 MiB


class ContainerError(Exception):
    """Raised when the stream does not conform to the WOODOO grammar."""


class Record:
    """One physical record in the stream."""

    __slots__ = (
        "offset",        # absolute offset of the 9-byte header
        "marker",        # byte0
        "index",         # LE16 byte1..2
        "length",        # LE32 byte3..6  (body byte count)
        "segment",       # byte7
        "flags",         # byte8
        "body_offset",   # absolute offset of body (offset + 9)
        "metadata",      # dict[str,str] for descriptor records, else None
        "meta_raw",      # raw ASCII metadata string for descriptors, else None
    )

    def __init__(self, offset, marker, index, length, segment, flags, body_offset):
        self.offset = offset
        self.marker = marker
        self.index = index
        self.length = length
        self.segment = segment
        self.flags = flags
        self.body_offset = body_offset
        self.metadata = None
        self.meta_raw = None

    @property
    def is_descriptor(self):
        return self.marker == MARKER_DESCRIPTOR

    @property
    def end(self):
        return self.body_offset + self.length


def _parse_metadata(raw):
    """Parse 'Key=Val;Key=Val;' ASCII into an ordered dict.

    Tolerant: ignores empty segments, keeps first value if a key repeats by
    storing into a plain dict in encounter order (Python dicts preserve order).
    Values may themselves contain no ';' (the field separator) by construction.
    """
    md = {}
    # Decode as latin-1 so every byte maps; metadata is ASCII in practice.
    text = raw.decode("latin-1", errors="replace")
    for chunk in text.split(";"):
        if not chunk:
            continue
        eq = chunk.find("=")
        if eq < 0:
            # Malformed fragment (no '='); stash under a synthetic key so we
            # don't silently lose data, but don't crash.
            md.setdefault("_raw", "")
            md["_raw"] += chunk
            continue
        key = chunk[:eq]
        val = chunk[eq + 1:]
        md[key] = val
    return md


def iter_records(fh, filesize):
    """Yield Record objects by walking the stream from offset 0.

    For descriptor (0x02) records the ASCII metadata body is read and parsed
    (small, bounded).  Data-record bodies are NOT read here -- only their header
    fields and offsets -- so this is cheap to iterate over GB files.

    Raises ContainerError on a malformed/truncated stream.  After the final
    record, the caller should confirm position == filesize (leftover == 0).
    """
    pos = 0
    while pos < filesize:
        remaining = filesize - pos
        if remaining < HEADER_LEN:
            raise ContainerError(
                "truncated record header at offset 0x%X: only %d byte(s) left, "
                "need %d" % (pos, remaining, HEADER_LEN)
            )
        fh.seek(pos)
        hdr = fh.read(HEADER_LEN)
        if len(hdr) != HEADER_LEN:
            raise ContainerError(
                "short read of record header at offset 0x%X" % pos
            )

        marker = hdr[0]
        index = hdr[1] | (hdr[2] << 8)                 # LE16
        length = (hdr[3] | (hdr[4] << 8) |
                  (hdr[5] << 16) | (hdr[6] << 24))     # LE32
        segment = hdr[7]
        flags = hdr[8]

        body_offset = pos + HEADER_LEN
        body_end = body_offset + length
        if body_end > filesize:
            raise ContainerError(
                "record at offset 0x%X (marker 0x%02X, idx 0x%04X) declares "
                "body length 0x%X running to 0x%X, past EOF 0x%X"
                % (pos, marker, index, length, body_end, filesize)
            )

        rec = Record(pos, marker, index, length, segment, flags, body_offset)

        if marker == MARKER_DESCRIPTOR:
            if length > _MAX_META_INMEM:
                raise ContainerError(
                    "descriptor at offset 0x%X has implausibly large metadata "
                    "length 0x%X" % (pos, length)
                )
            fh.seek(body_offset)
            raw = fh.read(length)
            if len(raw) != length:
                raise ContainerError(
                    "short read of descriptor metadata at offset 0x%X" % body_offset
                )
            rec.meta_raw = raw
            rec.metadata = _parse_metadata(raw)

        yield rec
        pos = body_end

    # Loop exits with pos == filesize on a clean walk.  pos may be left for the
    # caller to inspect; we expose it via the generator's StopIteration-free
    # contract by simply not raising here.


def _sanitize_component(name):
    """Make one path component safe for the local filesystem."""
    name = name.strip()
    # Replace anything outside a conservative allow-list.
    name = re.sub(r"[^A-Za-z0-9._\-]", "_", name)
    if name in ("", ".", ".."):
        name = "_"
    return name


def _rel_target_path(target_path):
    """Turn a metadata TargetPath (absolute QNX path like /mnt/data/...) into a
    SAFE relative path under outdir.  Strips leading slashes, sanitizes each
    component, drops '.'/'..' so extraction can never escape outdir.
    """
    parts = []
    for comp in target_path.replace("\\", "/").split("/"):
        if comp in ("", ".", ".."):
            continue
        parts.append(_sanitize_component(comp))
    return parts


def _group_iter(fh, filesize):
    """Walk physical records and group them into logical payloads.

    A group = one descriptor (0x02) followed by zero or more data records
    (marker != 0x02) up to the next descriptor.  Data records appearing with NO
    preceding descriptor (only the very first 0x01 file-header record in
    practice) are emitted as their own anonymous group.

    Yields tuples (descriptor_or_None, [data_records], final_pos_after_group).
    The generator also tracks and finally reports the end position via the
    returned attribute on the generator object is not possible cleanly, so the
    caller separately verifies EOF using the last record's .end.
    """
    pending_desc = None
    pending_data = []

    def flush():
        nonlocal pending_desc, pending_data
        if pending_desc is None and not pending_data:
            return None
        out = (pending_desc, pending_data)
        pending_desc = None
        pending_data = []
        return out

    for rec in iter_records(fh, filesize):
        if rec.is_descriptor:
            flushed = flush()
            if flushed is not None:
                yield flushed
            pending_desc = rec
        else:
            if pending_desc is None and not pending_data:
                # Orphan data record (the 0x01 file-header is the typical case).
                # Emit immediately as its own group so nothing is lost.
                yield (None, [rec])
            else:
                pending_data.append(rec)
    flushed = flush()
    if flushed is not None:
        yield flushed


def _meta_get(md, key):
    if not md:
        return ""
    return md.get(key, "")


def cmd_list(image_path):
    filesize = os.path.getsize(image_path)
    last_end = 0
    n = 0
    with open(image_path, "rb") as fh:
        for rec in iter_records(fh, filesize):
            md = rec.metadata if rec.is_descriptor else None
            name = _meta_get(md, "Name")
            tag = _meta_get(md, "Tag")
            qid = _meta_get(md, "QueueId")
            tpath = _meta_get(md, "TargetPath")
            print(
                "idx=0x%04X marker=0x%02X seg=%d metalen=%s payloadlen=%s "
                "Name=%s Tag=%s QueueId=%s TargetPath=%s"
                % (
                    rec.index,
                    rec.marker,
                    rec.segment,
                    (rec.length if rec.is_descriptor else 0),
                    (0 if rec.is_descriptor else rec.length),
                    name,
                    tag,
                    qid,
                    tpath,
                )
            )
            last_end = rec.end
            n += 1
    leftover = filesize - last_end
    sys.stderr.write(
        "[list] %s: %d record(s), end=0x%X, filesize=0x%X, leftover=%d\n"
        % (image_path, n, last_end, filesize, leftover)
    )
    if leftover != 0:
        raise ContainerError(
            "stream did not end at EOF: leftover %d byte(s)" % leftover
        )


def _copy_payload(fh, data_records, out_fh, hasher):
    """Stream the concatenated bodies of data_records into out_fh, updating
    hasher.  Returns total bytes written.
    """
    total = 0
    for rec in data_records:
        remaining = rec.length
        fh.seek(rec.body_offset)
        while remaining > 0:
            chunk = fh.read(min(_COPY_CHUNK, remaining))
            if not chunk:
                raise ContainerError(
                    "short read of payload body at offset 0x%X (record idx "
                    "0x%04X)" % (rec.body_offset, rec.index)
                )
            out_fh.write(chunk)
            hasher.update(chunk)
            total += len(chunk)
            remaining -= len(chunk)
    return total


def cmd_extract(image_path, outdir):
    filesize = os.path.getsize(image_path)
    os.makedirs(outdir, exist_ok=True)
    manifest_path = os.path.join(outdir, "_manifest.tsv")

    last_end = 0
    used_names = {}  # collision avoidance for derived filenames

    def unique_path(rel_parts):
        """Resolve a relative path under outdir, ensuring uniqueness."""
        rel = os.path.join(*rel_parts) if rel_parts else "_"
        full = os.path.join(outdir, rel)
        base = full
        i = 1
        while full in used_names:
            root, ext = os.path.splitext(base)
            full = "%s.%d%s" % (root, i, ext)
            i += 1
        used_names[full] = True
        return full

    with open(image_path, "rb") as fh, open(manifest_path, "w", encoding="utf-8") as man:
        man.write(
            "idx\tname\ttag\tqueueid\ttargetpath\tpayload_offset\t"
            "payload_len\tsha1\n"
        )
        for desc, data_records in _group_iter(fh, filesize):
            # Track furthest end for the EOF check.
            if desc is not None:
                last_end = max(last_end, desc.end)
            for d in data_records:
                last_end = max(last_end, d.end)

            md = desc.metadata if desc is not None else None
            name = _meta_get(md, "Name")
            tag = _meta_get(md, "Tag")
            qid = _meta_get(md, "QueueId")
            tpath = _meta_get(md, "TargetPath")
            idx = (desc.index if desc is not None
                   else (data_records[0].index if data_records else 0))

            if not data_records:
                # Pure script/command descriptor: no payload to extract.  Record
                # it in the manifest with empty payload fields for completeness.
                man.write(
                    "0x%04X\t%s\t%s\t%s\t%s\t\t0\t\n"
                    % (idx, name, tag, qid, tpath)
                )
                continue

            # Decide destination path.
            if tpath:
                rel_parts = _rel_target_path(tpath)
                if name:
                    rel_parts = rel_parts + [_sanitize_component(name)]
                elif not rel_parts:
                    rel_parts = ["idx_0x%04X.bin" % idx]
            elif name:
                rel_parts = [_sanitize_component(name)]
            else:
                rel_parts = ["idx_0x%04X.bin" % idx]

            dest = unique_path(rel_parts)
            os.makedirs(os.path.dirname(dest) or outdir, exist_ok=True)

            hasher = hashlib.sha1()
            payload_offset = data_records[0].body_offset
            with open(dest, "wb") as out_fh:
                payload_len = _copy_payload(fh, data_records, out_fh, hasher)

            man.write(
                "0x%04X\t%s\t%s\t%s\t%s\t0x%X\t%d\t%s\n"
                % (
                    idx, name, tag, qid, tpath,
                    payload_offset, payload_len, hasher.hexdigest(),
                )
            )

    leftover = filesize - last_end
    sys.stderr.write(
        "[extract] %s -> %s: end=0x%X, filesize=0x%X, leftover=%d\n"
        % (image_path, outdir, last_end, filesize, leftover)
    )
    if leftover != 0:
        raise ContainerError(
            "stream did not end at EOF: leftover %d byte(s)" % leftover
        )


def main(argv):
    ap = argparse.ArgumentParser(
        prog="nbt_container.py",
        description="Parse/extract Harman WOODOO/IOC-BOLO NBT Evo flash containers.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list records (one line per record)")
    p_list.add_argument("image")

    p_ext = sub.add_parser("extract", help="extract payloads to outdir")
    p_ext.add_argument("image")
    p_ext.add_argument("outdir")

    args = ap.parse_args(argv)

    try:
        if args.cmd == "list":
            cmd_list(args.image)
        elif args.cmd == "extract":
            cmd_extract(args.image, args.outdir)
    except ContainerError as e:
        sys.stderr.write("ERROR: %s\n" % e)
        return 2
    except BrokenPipeError:
        # Allow piping `list` into head, etc.
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# ---- payload location + extraction (added for the toolkit) ----

def locate_payload(image_path, name):
    """Return [(body_offset, length), ...] spans of the payload whose descriptor Name (or TargetPath
    basename) == name. Concatenated, these are the file's bytes inside the container; a single-segment
    file has one span. Raises ContainerError if not found."""
    filesize = os.path.getsize(image_path)
    with open(image_path, "rb") as fh:
        for desc, data in _group_iter(fh, filesize):
            if desc is None:
                continue
            md = desc.metadata
            nm = _meta_get(md, "Name")
            tp = _meta_get(md, "TargetPath")
            base = nm or (tp.rstrip("/").rsplit("/", 1)[-1] if tp else "")
            if name in (nm, base):
                return [(r.body_offset, r.length) for r in data]
    raise ContainerError("no payload named %r in %s" % (name, image_path))


def extract_payload(image_path, name, out_path):
    """Write the named payload's bytes (the file as it lives inside the container, all its data records
    concatenated in stream order) to out_path. This is how you get a stock `NBTCarHU` / `starter.cfg`
    out of your own container so you can edit it and re-wrap it (see patch.py). Returns the byte count."""
    spans = locate_payload(image_path, name)
    total = 0
    with open(image_path, "rb") as fin, open(out_path, "wb") as fout:
        for body_off, ln in spans:
            fin.seek(body_off)
            rem = ln
            while rem > 0:
                chunk = fin.read(min(_COPY_CHUNK, rem))
                if not chunk:
                    raise ContainerError("short read of payload %r body" % name)
                fout.write(chunk)
                total += len(chunk)
                rem -= len(chunk)
    return total


# ---- build a minimal NO-SIGNATURE file-copy container (the flashable artifact) ----
#
# This is the container you actually flash. Both worked patches (OPT_DEBUG and the blobB trust-anchor
# swap) are delivered this way, because the head unit's SwdlMaster finalizer short-circuits to ACCEPT
# when NO signature record is present (`mbSignaturePresent == 0`): it then routes the stream to the
# on-device file-copy job, which writes the data to <TargetPath>/<Name>. A signature, IF present, is
# verified over the WHOLE body, so a signed-but-modified stock container is REJECTED — which is why a
# surgical in-place edit of a signed `.bin` is NOT flashable, and this minimal rebuild is. See
# 01-how-flashing-works.md and 02-authoring-patches.md.

_MARK_START = 0x01
_MARK_DESC = 0x02
_MARK_DATA = 0x04


def _record(marker, index, body, segment):
    import struct
    return struct.pack("<BHIBB", marker, index, len(body), segment, 0x00) + body


def build_filecopy_container(file_path, target_dir, name=None, index=0x0002, tag="FIL", cpu="Omap"):
    """Return (container_bytes, info) for a minimal no-signature file-copy container that delivers
    file_path to <target_dir>/<name> on the head unit via the on-device file-copy job.

    Three records, nothing else (no F0002000.nsw signature, no per-file .sign):
      0x01 stream-start envelope (1-byte body, verbatim shape)
      0x02 descriptor   TargetPath=<dir>;Name=<f>;Tag=FIL;CPU=Omap;
      0x04 data         <file bytes>

    target_dir decides the write model (see 02-authoring-patches.md): a LIVE path
    (/fs/sda0/opt/...) overwrites the live file in place (effective next boot); a STAGING path
    (/fs/sda0/repository/istep/opt/...) writes the repo copy and needs a separate linkIStep to go live.
    This function neither reads nor checks the path gate — validate/check_patch.py does."""
    with open(file_path, "rb") as f:
        body = f.read()
    if name is None:
        name = os.path.basename(file_path)
    if not target_dir.endswith("/"):
        target_dir += "/"
    meta = ("TargetPath=%s;Name=%s;Tag=%s;CPU=%s;" % (target_dir, name, tag, cpu)).encode("latin-1")
    rec0 = _record(_MARK_START, 0x0001, b"\x01", 1)   # stream-start envelope
    desc = _record(_MARK_DESC, index, meta, 1)        # one data record follows
    data = _record(_MARK_DATA, index, body, 1)        # the file payload
    blob = rec0 + desc + data
    return blob, {
        "name": name, "target_dir": target_dir, "target_full": target_dir + name,
        "index": index, "meta_len": len(meta), "body_len": len(body), "out_size": len(blob),
    }
