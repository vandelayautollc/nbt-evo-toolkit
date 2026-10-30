"""
Paths into YOUR OWN extracted HMI tree, and BMW's protobuf classes (recovered descriptor set).

The packager reads your own extracted HMI resources — it ships none. The HMI is two software units:
the BMW-brand unit (SWFL 00002719) and the common unit (SWFL 00002720); each extracts to a
``…/opt/hmi/ID5/data/ro`` tree plus a signed ``manifest_hmi*.xml``. Point the toolkit at yours:

    export NBTEVO_HMI_ROOT=/path/you/arrange       # expects, underneath it:
        bmw/ro/      bmw/manifest_hmiBMW.xml        (from your 00002719 unit)
        common/ro/   common/manifest_hmiCOMMON.xml  (from your 00002720 unit)

  …or set the four paths explicitly:
        NBTEVO_HMI_BMW_RO, NBTEVO_HMI_BMW_MANIFEST, NBTEVO_HMI_COMMON_RO, NBTEVO_HMI_COMMON_MANIFEST

The protobuf descriptor set (``hmi_descriptors.bin``, our recovered schema) ships next to this file.
"""
import hashlib
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DESCRIPTORS = os.path.join(HERE, "hmi_descriptors.bin")   # shipped: our recovered BMW HMI schema

VEHICLES = "bmw/widgetasset/vehicles"                      # series folders, relative to ro/
BRAND_REGISTRY = "bmw/widget/variantregistry.pbvar"        # BMW's per-series registry entries
LINES = ("id5", "id6l")                                    # root 7 = bmw/<line>/, picked by HMI-version coding


class HmiTreeNotConfigured(RuntimeError):
    pass


_paths_cache = {}


def _env(name):
    v = os.environ.get(name)
    return v if v else None


def _paths():
    """Resolve (bmw_ro, bmw_manifest, common_ro, common_manifest) from the environment, once."""
    if _paths_cache:
        return _paths_cache
    root = _env("NBTEVO_HMI_ROOT")
    bmw_ro = _env("NBTEVO_HMI_BMW_RO") or (os.path.join(root, "bmw", "ro") if root else None)
    bmw_man = _env("NBTEVO_HMI_BMW_MANIFEST") or (os.path.join(root, "bmw", "manifest_hmiBMW.xml") if root else None)
    common_ro = _env("NBTEVO_HMI_COMMON_RO") or (os.path.join(root, "common", "ro") if root else None)
    common_man = _env("NBTEVO_HMI_COMMON_MANIFEST") or (os.path.join(root, "common", "manifest_hmiCOMMON.xml") if root else None)
    missing = [n for n, v in [("bmw ro", bmw_ro), ("bmw manifest", bmw_man),
                              ("common ro", common_ro), ("common manifest", common_man)] if not v or not os.path.exists(v)]
    if missing:
        raise HmiTreeNotConfigured(
            "HMI tree not configured (or paths don't exist): " + ", ".join(missing) + ".\n"
            "Point the packager at your own extracted HMI tree — set NBTEVO_HMI_ROOT (see hmi.py),\n"
            "or the four NBTEVO_HMI_* paths. This toolkit ships no HMI resources; you supply your own."
        )
    _paths_cache.update(bmw_ro=bmw_ro, bmw_manifest=bmw_man, common_ro=common_ro, common_manifest=common_man)
    return _paths_cache


def ro():
    """The BMW-brand ro/ root (where bmw/widgetasset/… lives)."""
    return _paths()["bmw_ro"]


def index_path(line):
    """Root 7's widget-asset index — the only place asset ids are registered (CHmiResourceScanner::scan)."""
    return f"bmw/{line}/widgetasset/resources.pbr"


def registry_path(line):
    """Root 7's main registry file: loaded last of all six, absent in the firmware."""
    return f"bmw/{line}/widget/variantregistry.pbvar"


_classes = {}


def proto(name):
    """Message class for a BMW type, e.g. proto('HmiResource.TResourceDefinition'). Needs only the descriptor set."""
    if not _classes:
        from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
        fds = descriptor_pb2.FileDescriptorSet.FromString(open(DESCRIPTORS, "rb").read())
        pool = descriptor_pool.DescriptorPool()
        pending, done = list(fds.file), set()
        while pending:
            for f in list(pending):
                if all(d in done for d in f.dependency):
                    pool.Add(f); done.add(f.name); pending.remove(f)
        _classes["pool"] = pool
        _classes["factory"] = message_factory
    if name not in _classes:
        _classes[name] = _classes["factory"].GetMessageClass(_classes["pool"].FindMessageTypeByName(name))
    return _classes[name]


def pool():
    """The descriptor pool holding BMW's recovered schemas — for text_format.Parse of extension fields
    (e.g. the authoring layer's expression/curve messages). Loads the descriptor set on first use."""
    if "pool" not in _classes:
        proto("HmiScenegraph.TScene")  # any type; populates _classes["pool"]
    return _classes["pool"]


def _tree(rel):
    """(ro root, signed manifest) holding [rel]: ro/common/ ships in its own software unit."""
    p = _paths()
    if rel.startswith("common/"):
        return p["common_ro"], p["common_manifest"]
    return p["bmw_ro"], p["bmw_manifest"]


def read(rel):
    return open(os.path.join(_tree(rel)[0], rel), "rb").read()


def manifest_sha1(rel):
    """The signed manifest's hash for a file under ro/ (its 'md5' attribute is really SHA-1)."""
    want = "opt/hmi/ID5/data/ro/" + rel
    stack = []
    for m in re.finditer(r'<dir [^>]*name="([^"]+)"[^>]*>|</dir>|<file ([^>]*)/>', open(_tree(rel)[1]).read()):
        if m.group(0).startswith("</dir"):
            stack.pop()
        elif m.group(1):
            stack.append(m.group(1))
        else:
            a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(2)))
            if "/".join(stack + [a["name"]]) == want:
                return a.get("md5")
    return None


def stock(rel):
    """A file from your extracted firmware, refused unless it matches the signed manifest."""
    data = read(rel)
    want = manifest_sha1(rel)
    if want is None or hashlib.sha1(data).hexdigest() != want:
        raise ValueError(f"{rel}: file does not match {os.path.basename(_tree(rel)[1])} ({want})")
    return data


def stock_series():
    return sorted(os.listdir(os.path.join(ro(), VEHICLES)))
