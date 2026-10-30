# 02 · Packaging and installing a custom car

You've authored a model — either by hand (meshes with `rsvi.py`) or, more usually, with the
**authoring layer** (`tools/author.py` + `tools/mesh.py` + `tools/widget_expr.py`), which mutates a
copy of a stock series folder to add your own geometry, materials and animation bindings. The
[blueprint example](examples/blueprint/) shows that end to end. This doc turns the resulting
**chassis folder** into an installable `.nbtcar` and puts it on the head unit — on your own car, as
its own model, without touching a stock file.

## What the packager needs

1. **A chassis folder** — `vehicle/` + `camera_crane/`, each with `scene.pbx` + `widget.pbw` + its
   `meshes/` `bitmaps/` `shaders/`, built on a stock series as a **template** (default `F30`, so it
   inherits working pivots and animation wiring). The packager checks the scene doesn't name files
   the folder lacks.
2. **Your own extracted HMI tree.** The packager rebuilds the resource index bundles from your own
   firmware; it ships none. It is two software units — the BMW-brand unit (SWFL `00002719`) and the
   common unit (`00002720`) — each extracting to a `…/opt/hmi/ID5/data/ro` tree plus a signed
   `manifest_hmi*.xml`. Point the toolkit at yours:

   ```bash
   export NBTEVO_HMI_ROOT=/path/you/arrange      # expects underneath it:
   #   bmw/ro/     bmw/manifest_hmiBMW.xml        (from your 00002719 unit)
   #   common/ro/  common/manifest_hmiCOMMON.xml  (from your 00002720 unit)
   # …or set NBTEVO_HMI_BMW_RO / _BMW_MANIFEST / _COMMON_RO / _COMMON_MANIFEST explicitly.
   ```

   The protobuf schema (`packager/hmi_descriptors.bin`, our recovered descriptor set) ships with the
   toolkit, so you don't supply that.

## Prove the setup before you build: `--selftest`

The generator can rebuild **every stock series' index bundles byte-for-byte** from your own tree. If
that passes, your HMI tree is intact and the generator matches your firmware — the trust anchor
before you build anything new:

```bash
python -m capabilities.vehicle_models.packager.package --selftest
# id5:  26 series rebuilt byte-identically; other layouts: F06 F12 …
# id6l: 26 series rebuilt byte-identically; …
# selftest ok
```

(The "other layouts" are older series that don't use the five-bundle layout — they just aren't
templates. The `stock()` reader also refuses any file that doesn't match the signed manifest, so a
mismatched extraction fails loudly here rather than producing a bad package.)

## Build the package

```bash
python -m capabilities.vehicle_models.packager.package \
    --id WARTHOG --name "M12 Warthog" --folder warthog/out/F30 [--template F30] [--preview shot.png]
# WARTHOG: N files, X KiB -> ./warthog.nbtcar (Y KiB, sha256 …)
```

The `.nbtcar` is a zip containing `car.json`, `bundles.pb` (the ungated index bundles for every
file under the model root), `registry.pb` (one unconditional entry pointing the asset ids at your
model), and `files/…` (the model as the head unit gets it). Builds are byte-deterministic.

## Install on the head unit (the exact steps — no script needed)

This is a file install over SSH, on-car-verified. You don't need a packaged installer; you need to
do these steps precisely, because **one of them has an integrity trap**. Read the LMPC note before
step 3. The shared SSH mechanics (reaching the dev shell, `mount -uw`, the rename-over rule,
`appreset`, restoring the mount) are in
[docs/staging-files-over-ssh.md](../../docs/staging-files-over-ssh.md); this section is the
custom-car specifics on top of it.

### 0. Get a shell and locate the tree

SSH to the HU's **QNX dev interface** (the second IP — *not* the diagnostic endpoint; see
[docs/architecture.md](../../docs/architecture.md) §Networking). Then **discover** the resource
root rather than assuming its path — find the directory that holds the root-7 indexes:

```sh
# on the HU: find the widget-asset indexes (one per brand/line that exists)
ls -d /fs/sda0/**/widgetasset/resources.pbr 2>/dev/null   # or: find /fs/sda0 -name resources.pbr -path '*widgetasset*'
# typically: <ro>/bmw/id5/…, <ro>/bmw/id6l/…  (+ bmwm/, rr/ on some units)
```

Call that resource root `$RO` and each index `$RO/<brand>/<line>/widgetasset/resources.pbr`. Patch
**every** index you find (the model is ungated, so patching all lines/brands makes it show on any
car). The HMI filesystem is on `/fs/sda0`; remount it read-write for the install (safe to do, and
you put it back):

```sh
mount -uw /fs/sda0            # remount read-write (QNX; confirm the flag your HU's mount accepts)
```

### 1. Copy the model files

Unpack the package's `files/…` into `$RO/vae/vehicles/<ID>/` (stage into a temp dir, then move into
place, so a half-copy is never live):

```sh
mkdir -p "$RO/vae/vehicles/.incoming"
# scp / tar the package's files/ into $RO/vae/vehicles/.incoming, then:
mv "$RO/vae/vehicles/.incoming" "$RO/vae/vehicles/<ID>"
```

### 2. ⚠️ LMPC — do NOT edit the index in place

`resources.pbr` is a **manifest-listed file hashed by LinkManagerHU**; editing it in place changes
the hash and raises a DTC (see [LMPC in architecture.md](../../docs/architecture.md)). The safe move
is a **rename-over**: build the new index as a *new* file and `mv` it over the path, keeping the
original (still hard-linked to the signed repo copy, whose inode — and hash — is untouched).

A repeated protobuf field concatenates, so appending `bundles.pb` is just `cat`:

```sh
for idx in $RO/bmw/id5/widgetasset/resources.pbr $RO/bmw/id6l/widgetasset/resources.pbr; do
    cat "$idx" bundles.pb > "$idx.vae-new"      # stock bytes stay a byte-exact prefix
    ln  "$idx" "$idx.vae-orig"                  # keep the signed hard-link as the backup
    mv  "$idx.vae-new" "$idx"                   # rename-over: new inode, signed inode untouched
done
```

(Guard first if you want to be sure you're not re-installing: `diff "$idx" "$idx.vae-orig"` should
differ only by your appended bundles. Note the HU's busybox has `diff` but **no `cmp`, `which`, or
`head`** — use what's there.)

### 3. Write the registry override

`variantregistry.pbvar` does **not** exist in the firmware (nothing to trip LMPC), so just write it
— it loads last and selects your model for every series:

```sh
for line in id5 id6l; do cp registry.pb "$RO/bmw/$line/widget/variantregistry.pbvar"; done
```

### 4. Restart the HMI (the proven way)

`appreset` restarts the HMI without a full reboot. Run it **detached** so it survives your SSH
channel closing, with the HU's library path set:

```sh
LD_LIBRARY_PATH=/opt/car/lib on -d /opt/car/bin/OnOffDSICommander appreset
```

`appreset` wipes `/tmp`, so drop a marker there first and poll for its disappearance to know the
restart happened — **don't** detect it by PID: QNX's deterministic start order gives `HmiMain3D` the
**same PID** again. After it comes back, your model is the car on the vehicle-status screen.

### Uninstall (reverse, equally LMPC-safe)

```sh
mount -uw /fs/sda0
for idx in $RO/bmw/*/widgetasset/resources.pbr; do [ -f "$idx.vae-orig" ] && mv "$idx.vae-orig" "$idx"; done
rm -f  $RO/bmw/*/widget/variantregistry.pbvar
rm -rf "$RO/vae/vehicles/<ID>"
LD_LIBRARY_PATH=/opt/car/lib on -d /opt/car/bin/OnOffDSICommander appreset
```

Everything you touched was added or renamed, never written into a stock file, so this returns the
unit byte-for-byte to stock. A thin wrapper script that runs exactly these steps is an optional
convenience, not a requirement — the steps above are the whole of it.

## Not yet ported

- **`--hero`** (replacing the 2D *My Vehicle* picture): the research-tree version renders the hero
  PNGs with a headless browser (Playwright + Chromium). It's an optional extra on top of the 3D
  model and isn't ported here yet.
- **A wrapper script** that runs the install/uninstall steps above in one command — optional; the
  steps are complete as written and an agent can execute them directly.
- **The WebGL previewer** (render a model in a browser before install) — handy but optional.
