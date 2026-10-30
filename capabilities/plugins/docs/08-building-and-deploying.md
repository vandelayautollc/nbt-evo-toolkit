# 08 — Building & Deploying a Plugin

> **Authorization / scope.** Everything here was reconstructed from an offline flash
> carve and owner-authorized work on the author's own titled vehicle. It is written for
> a developer building a plugin for **their own** NBT-Evo head unit. Nothing in this
> guide requires touching a network or a vehicle you do not own.

This is the toolchain-and-deployment doc: how to cross-compile your `lib<Name>.so`, lay
the three plugin files out on the unit, get the HMI to discover them, prove the load, and
back it all out. It assumes you already have your `<Name>.manifest`, `<Name>.xml`
(DescFile), and C++ source — those are covered in the companion manifest, DescFile/XML,
and ABI docs. Read this one end-to-end before your first build; the validation ladder in
§6 is what turns "it compiled" into "the HMI accepted it."

**Status legend used throughout:**

| Tag | Meaning |
|---|---|
| **VERIFIED** | Confirmed from the carve or observed on the author's unit. |
| **RECONSTRUCTED** | Hand-reconstructed ABI (the `bmw_*.h` headers). Correct enough that a real plugin loads and runs, but not an OEM header. |

---

## 0. What a build produces (recap)

A plugin is **three loose files in one directory** that the HMI (`HmiMain3D`) discovers,
`dlopen()`s, and runs as a menu app:

| File | What it is | Produced by |
|---|---|---|
| `lib<Name>.so` | Compiled ARM/QNX shared object exporting the C symbol `pluginAppInfo` | This doc (cross-compile) |
| `<Name>.manifest` | Loader config (XML): name, type, `.so` file, `autoStart`, dependencies, `DescFile` | You (see manifest doc) |
| `<Name>.xml` | The DescFile: menu entry, screens, components, actions, models | You (see DescFile doc) |

One naming rule that bites people at deploy time: the manifest's `<file>` tag names the
**base name without the `lib` prefix or `.so` suffix**, and the loader expands it to
`lib<base>.so`. In the reference plugin the manifest says `<file>{pluginDir}/Diagnostics</file>`
and the built object is `libDiagnostics.so`
(`capabilities/plugins/reference/example-plugin/Diagnostics.manifest:5`; built object confirmed
`libDiagnostics.so`, `file` → *ELF 32-bit LSB shared object, ARM*). The rule holds across
all three RA plugins in the carve: `SecurityMenu` → `libSecurityMenu.so`, `ActiveSeating`
→ `libActiveSeating.so` (`.../PluginsCoded/{SecurityMenu,ActiveSeating}/` listings).

> **Don't confuse this with `hmiplugins/`.** A grep of the carve turns up a *second*,
> unrelated plugin root, `.../data/ro/hmiplugins/`, holding `A4APlugin.xml` /
> `RemotingPlugin.xml` and `libhmia4a.so` / `libhmiremoting.so`. Those are **not** RA
> plugins — they are `<Bundle>/<Plugin>` service bundles for RHMI/remoting infrastructure,
> wired by `exportedSymbolName` / `implementedInterface` (`A4APlugin.xml`,
> `RemotingPlugin.xml`) — a **distinct** mechanism from both the RA-plugin framework this
> SDK teaches and the `libhmiplugin.so` device-abstraction layer, and one this SDK does
> **not** cover.
> They neither use the `pluginAppInfo` entry point nor the `<Name>.manifest` schema, so do
> not treat them as counter-examples to anything below.

---

## 1. Prerequisites

### 1.1 Cross toolchain — QNX SDP 6.5.0 / gcc 4.4.2

The NBT-Evo HMI is a **QNX 6.5.0** system and the OEM framework libraries are **ARM
EABI5** objects (`file` on `libAppFramework.A.so` → *ELF 32-bit LSB shared object, ARM,
EABI5 version 1 (SYSV) ... stripped*). To produce a compatible object you build with the
matching QNX Software Development Platform: **QNX SDP 6.5.0, whose ARM C++ driver is
`ntoarm-g++` (GCC 4.4.2)**.

The compiler *version* is not a loose recommendation — it is carve-verified. Both OEM
framework shared objects carry their build compiler in their ELF `.comment` section:

```
$ readelf -p .comment libAppFramework.A.so
  [     0]  GCC: (GNU) 4.4.2
$ readelf -p .comment libCoreFramework.A.so
  [     0]  GCC: (GNU) 4.4.2
```

That is direct evidence **from your own carve** that the framework was built with gcc
4.4.2, which is exactly what QNX SDP 6.5.0's `ntoarm-g++` provides (VERIFIED: the SDP
`env.sh` selects the 6.5.0 ARM toolchain; `ntoarm-g++ --version` → `ntoarm-g++ (GCC) 4.4.2`).
Matching it matters because the reconstructed headers rely on gcc 4.x C++ ABI details
(name mangling, class layout, vtable emission) that line up with what the framework libs
were built with. Building with a modern g++ will mangle and lay out incompatibly.

The SDP ships an environment script you `source` once per shell to put the cross tools on
`PATH`. It sets `QNX_HOST` / `QNX_TARGET` / `PATH` (generalized — your install prefix will
differ):

```sh
# QNX SDP 6.5.0 (Linux host). Source before building.
export QNX_HOST=/path/to/qnx650/host/linux/x86
export QNX_TARGET=/path/to/qnx650/target/qnx6
export PATH=/path/to/qnx650/armbin:$QNX_HOST/usr/bin:$PATH
```

After sourcing it, `ntoarm-g++` is on your `PATH`.

### 1.2 The two framework libraries — from **your own** carve

Your plugin references `bmw::` symbols it does not define. You resolve them by linking
against the OEM framework shared objects from your own unit's flash:

- `.../opt/hmi/ID5/lib/libAppFramework.A.so`
- `.../opt/hmi/ID5/lib/libCoreFramework.A.so`

You need **both**, because the symbols split across them — VERIFIED with `nm -DC`:

| Symbol you call | Lives in |
|---|---|
| `bmw::PluginApp::PluginApp(...)` ctor (`_ZN3bmw9PluginAppC1E...` @ `0x6f80`) | `libAppFramework.A.so` |
| `bmw::PluginApp::updateModel(uint, DataTableBase const&)` @ `0x539c` | `libAppFramework.A.so` |
| `bmw::PluginApp::setProperty` @ `0x54a4` / `addHandler` @ `0x5970`,`0x5db0` / `post` @ `0x6024` | `libAppFramework.A.so` |
| `bmw::DataTableBase::DataTableBase(Map<uint,Variant>*,uint)` @ `0xaa24`, `::clear()` @ `0xaa90` | `libCoreFramework.A.so` |
| `bmw::Variant::operator=(Variant const&)` @ `0x9d04` and friends | `libCoreFramework.A.so` |

These files are **not redistributable** — each developer carves their own copy from their
own unit. They are also **not** copied to the target at deploy time: identical copies
already live on the HU at `/opt/hmi/ID5/lib/`, and that is where the runtime linker
resolves your symbols when `HmiMain3D` `dlopen()`s you. You link against the carved copies
only so the build's symbol references have something to bind to.

### 1.3 Onboard shell + writable-filesystem access (precondition, not taught here)

Dropping files on the unit and restarting the HMI requires root shell and a writable
data partition on the HU. On the author's unit this is provided by a **persistent
OPT_DEBUG enable** (a `starter.cfg` `RequestState` STOP→RUN change) — it is what gives
you ssh/telnet/qconn at all (the flash capability, [`../../flash_and_patching/`](../../flash_and_patching/)).
**That enable is a precondition of this guide, not part of it.** If your unit does not already permit shell
and file access, obtain it by your own means first; the rest of this doc assumes a root
shell on the HU and a data partition you can remount read-write.

---

## 2. The Makefile, line by line

The reference build is a short Makefile
(`capabilities/plugins/reference/example-plugin/Makefile`, flags at lines 6–7). Generalized for any
plugin:

```make
# Cross-build lib<Name>.so for NBT-Evo (QNX 6.5.0 / ARM). Source qnx650/env.sh first.
CXX      := ntoarm-g++
CARVE    := /path/to/your/carve/opt/hmi/ID5/lib
LIBS     := $(CARVE)/libAppFramework.A.so $(CARVE)/libCoreFramework.A.so
SRC      := myplugin.cpp
NAME     := MyPlugin

CXXFLAGS := -shared -fPIC -O2 -fno-strict-aliasing -Wall -fno-exceptions
LDFLAGS  := -Wl,--allow-shlib-undefined -Wl,-soname,lib$(NAME).so

lib$(NAME).so: $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) $(LIBS) $(LDFLAGS) -o $@

clean:
	rm -f lib$(NAME).so
```

Flag by flag:

| Flag | Why it is there |
|---|---|
| `-shared` | Emit a shared object (`.so`), not an executable. The loader `dlopen()`s it. |
| `-fPIC` | Position-independent code, required for a `dlopen`-able object. |
| `-O2` | Optimize. No ABI effect; purely size/speed. |
| `-fno-strict-aliasing` | **Essential.** The plugin punning-casts through the reconstructed layouts — e.g. `reinterpret_cast<bmw::IPluginApp*>(pluginApp)` (the base sits at offset 0), and the raw-buffer `Parcel`/`Variant` structs in `bmw_list.h`. Strict aliasing would let the optimizer assume those casts don't alias and miscompile the struct accesses. |
| `-Wall` | Warnings. No ABI effect. |
| `-fno-exceptions` | **Match the framework ABI.** The OEM framework is built without C++ exceptions. Compiling with exceptions would (a) emit unwind/personality-routine references that are undefined at `dlopen` and (b) risk throwing across the `extern "C"` `create`/`destroy` boundary into no-exceptions framework code — undefined behavior. Keeping it off keeps the object clean and the boundary safe. |
| `-Wl,--allow-shlib-undefined` | **The load-bearing linker flag.** See below. |
| `-Wl,-soname,lib<Name>.so` | Stamp the object's soname so the runtime linker identifies it by that name. Match it to the deployed filename. |

### Why `--allow-shlib-undefined`

You put `libAppFramework.A.so` and `libCoreFramework.A.so` on the link line so your own
`bmw::` references resolve. But **those framework libraries are themselves incomplete** —
they are stripped shared objects with their own undefined symbols that are only satisfied
later, inside the full `HmiMain3D` process (system libs, other HMI libraries, and the host
binary). By default `ld` walks the shared libraries you link against and errors if *their*
undefined symbols can't be resolved at link time. `--allow-shlib-undefined` suppresses
exactly that transitive check, deferring all such resolution to runtime — which is correct,
because at `dlopen()` time the HMI process has the complete library graph loaded. Without
this flag the link fails on framework-internal symbols you neither call nor can supply.

You can confirm your object is *supposed* to have unresolved `bmw::` symbols at link time —
they are what the HMI fills in at load. VERIFIED on the reference object:

```
$ nm -DCu libDiagnostics.so | grep bmw | head
 U bmw::BasicString<char>::BasicString(char const*)
 U bmw::DataTableBase::DataTableBase(bmw::Map<unsigned int, bmw::Variant>*, unsigned int)
 U bmw::PluginApp::updateModel(unsigned int, bmw::DataTableBase const&)
 U bmw::PluginApp::addHandler(unsigned int, bmw::Delegate<...> const&)
 ...
```

Those `U` (undefined) entries are not a bug — they are the plugin's contract with the
framework.

> **On the `$(LIBS)` positional form.** The two libraries are passed as plain file paths,
> not `-l` flags. That is deliberate: they carry an soname and a version suffix (`.A.so`)
> and are not on a standard `-L` search path, so naming the file directly is simplest and
> unambiguous.

---

## 3. Build and self-check the object

```sh
source /path/to/qnx650/env.sh
make
```

Then verify the object is well-formed **before** you ship it. Four cheap checks catch the
common mistakes:

**a) Correct architecture** — must be ARM 32-bit, matching the framework libs:

```
$ file libMyPlugin.so
libMyPlugin.so: ELF 32-bit LSB shared object, ARM, version 1 (ARM), dynamically linked, not stripped
```

**b) EABI attributes match the framework** — a matching `file` line is necessary but not
sufficient; confirm the ARM ABI build attributes line up with the libraries you linked
against. Dump both and eyeball the `Tag_ABI_*` / `Tag_CPU_*` rows — they should agree:

```
$ readelf -A libMyPlugin.so           # your object
$ readelf -A /path/to/carve/.../libAppFramework.A.so   # the framework it must bind to
# Compare the aeabi attribute rows (Tag_CPU_arch, Tag_ABI_VFP_args, Tag_ABI_PCS_*, ...).
```

If these diverge, your SDP/toolchain revision differs from the one the framework was built
with, and symbols that link cleanly against the carve may still fail to bind at runtime.
This is the concrete check behind the "match the toolchain" caveat in §1.1.

**c) The entry point is exported** — the loader `dlsym()`s the *un-mangled* C symbol
`pluginAppInfo`; if it's missing or mangled, the HMI logs
`Error: Plugin does not contain a pluginAppInfo entry point` (VERIFIED string in
`HmiMain3D`). It must appear as a defined, un-mangled `OBJECT`:

```
$ nm -DC libMyPlugin.so | grep pluginAppInfo
000039d8 D pluginAppInfo
$ readelf -sW libMyPlugin.so | grep pluginAppInfo
   68: 000039d8    24 OBJECT  GLOBAL DEFAULT   19 pluginAppInfo
```

The 24-byte size matches the six-field descriptor
(`{abiVersion, name, vendor, ifaceVersion, create, destroy}` — 4+4+4+4+4+4), which is what
the loader casts it to (RECONSTRUCTED layout, `bmw_abi.h:49-57`; the descriptor being read
by the loader is VERIFIED — the two error strings
`Error: Plugin does not contain a pluginAppInfo entry point` and
`Error: The plugin's pluginAppInfo entry point is invalid` are both present in `HmiMain3D`).
Because it's declared `extern "C"`, the name stays un-mangled:

```cpp
extern "C" PluginAppInfo pluginAppInfo = {
    1,                 // abiVersion  (RECONSTRUCTED: ctor appears to read low16=major, high16=minor)
    "MyPlugin",        // name
    "my-vendor",       // vendor
    1,                 // ifaceVersion
    my_create,
    my_destroy,
};
```

**d) The `bmw::` references are present and undefined** (the `nm -DCu` check from §2). If
they're *absent*, your `#include` of the reconstructed header is wrong; if they fail to
*bind at runtime*, the framework-lib versions on the HU differ from your carve.

---

## 4. Deployment layout

> The generic SSH-install mechanics — reaching the dev shell, remounting `/fs/sda0` read-write,
> the write-under-the-mount-point trap, `appreset`, verify, and restoring read-only — are the
> shared ones in [docs/staging-files-over-ssh.md](../../../docs/staging-files-over-ssh.md). This
> section covers the plugin-specific layout on top of that.

### 4.1 Where the files go

The HMI scans two sibling plugin roots under `.../opt/hmi/ID5/data/ro/`:

- `PluginsCoded/` — OEM plugins gated by vehicle coding (e.g. `SecurityMenu`,
  `ActiveSeating`).
- `Plugins/` — the plain (uncoded) scan directory. **This is where your plugin goes.**

Both path stems are VERIFIED as literals inside `HmiMain3D` (`strings` → `/Plugins`,
`/Plugins/`, `/PluginsCoded`). On the author's unit the `Plugins/` directory does not
exist out of the box and you create it (`capabilities/plugins/docs/08-building-and-deploying.md`).

Create one directory per plugin and drop the three files in it:

```
.../opt/hmi/ID5/data/ro/Plugins/
└── MyPlugin/
    ├── libMyPlugin.so
    ├── MyPlugin.manifest
    └── MyPlugin.xml
```

The `{pluginDir}` token in the manifest resolves to this directory, so
`<file>{pluginDir}/MyPlugin</file>` → `.../Plugins/MyPlugin/libMyPlugin.so` and
`<DescFile>{pluginDir}/MyPlugin.xml</DescFile>` → the DescFile beside it
(`Diagnostics.manifest:5,16`; OEM `SecurityMenu.manifest:5,16` uses the identical token).

> **Coded OEM plugins are signed; your dev plugin is not.** Each `PluginsCoded/` entry
> ships two extra files next to the `.so`/`.manifest`/DescFile that the uncoded dev route
> does **not** produce: `<Name>.p7b` (a PKCS#7 signature blob) and `<Name>.p12` (a PKCS#12
> certificate bundle) — VERIFIED, present for both `SecurityMenu` and `ActiveSeating`
> (`.../PluginsCoded/SecurityMenu/{SecurityMenu.p7b,SecurityMenu.p12}`,
> `.../PluginsCoded/ActiveSeating/{ActiveSeating.p7b,ActiveSeating.p12}`). This is the
> strongest carve evidence on the signing question, and it sharpens it: coded plugins in
> `PluginsCoded/` ship with a `.p7b`/`.p12` — but those are **A4A/RemoteApp PKI material**
> (the chain is `CN=a4a_app_Connected…`, issued by `a4a_root-ca-i`), **not a plugin-load
> input**. The load path reads neither file. Signing is **not enforced on plugin load**:
> `HmiMain3D`, `libhmiplugin.so` and `libhmicoding.so` link **no** cryptography (zero
> `libcrypto`/`PKCS7`/`X509` references), and the complete load-abort list contains no
> signature/cert/hash branch (see §6 and `01-architecture-and-loading.md §3.1`). Confirmed
> statically, and on-car: the owner's own **unsigned** plugin loaded from `Plugins/` on a
> stock unit.

> **Keep app-private assets and addresses out of the SDK layout.** A real plugin may ship
> extra files — a helper child binary, bitmaps, a text DB (the OEM `SecurityMenu` manifest
> adds `TextDBFile`, `ImageDBFile`, and a `Bitmaps/` `ImagePath`, `SecurityMenu.manifest:17-22`).
> Those belong to *your* app and are your concern, not part of the plugin mechanism. In
> particular, do not bake fixed network addresses or a specific vehicle's diagnostic
> endpoints into a plugin you share — the author's own plugin hardcodes a gateway address
> and a private scan-binary path in its `.cpp`, and those are deliberately **not** part of
> this SDK. Parameterize or omit them.

### 4.2 Push the files (generic)

Work on the HU as root. The data partition is mounted read-only in normal operation, so
remount it read-write first, then create the directory and copy the three files **under
that same mount point** — on the reference unit `/opt/hmi/ID5/data` lives on the remounted
data partition (`/fs/sda0`), so the plugin path and the mount you just made writable must
be the same filesystem:

```sh
# On the HU, as root. The writable data partition's mount point is unit-specific;
# it is the filesystem that carries /opt/hmi/ID5/data. On the reference unit it is
# /fs/sda0, and /opt/... resolves onto it. Substitute your unit's mount name.
mount -uw /fs/sda0
mkdir -p /fs/sda0/opt/hmi/ID5/data/ro/Plugins/MyPlugin
# copy libMyPlugin.so, MyPlugin.manifest, MyPlugin.xml into that directory
sync
```

> Write the files under the **remounted mount point** (here `/fs/sda0/opt/...`), not a
> bare `/opt/...`, unless you have confirmed `/opt` on your unit is that same partition. If
> `/opt` is a different filesystem, a bare `mkdir -p /opt/...` lands on the wrong mount and
> the HMI — which reads `/fs/sda0/opt/...` — never sees the plugin. The reference
> deploy does all of its `mkdir`/copy/`rm` under `/fs/sda0/opt/hmi/ID5/data/ro/Plugins/...`
> (`capabilities/plugins/docs/08-building-and-deploying.md`).

The transport (scp/ssh/`cat`-pipe, a share, a USB copy) is up to you and your unit's
access method — the reference workflow pipes the files in over an existing root ssh
session (`DEPLOY.md`, "cat-pipe the three files over ssh"). Nothing about the plugin
mechanism depends on the transport.

---

## 5. Trigger discovery

The plugin roots are scanned when the HMI starts. To pick up a newly-dropped plugin,
restart the HMI process — **either**:

- **Restart `HmiMain3D`.** On the author's unit the process is under a watchdog and
  respawns automatically after it's killed (~10–30 s), re-scanning the plugin dirs on the
  way up (`DEPLOY.md`, "Restart HmiMain3D (slay + auto-respawn)"). **or**
- **Reboot the unit.**

A restart is faster and less disruptive; a reboot is the fallback if your unit does not
auto-respawn the HMI. (The exact respawn timing and the responsible watchdog are observed
on the author's unit, not derivable from the carve.)

---

## 6. Validation ladder

Verify the load in stages, from "the OS mapped my code" up to "the framework rendered my
menu." Each rung isolates a different failure. The reference plugin writes marker files
from inside itself for the first two rungs (`diagnostics.cpp:14-40`); `/tmp` is RAM on the
HU, so the markers are readable over your shell while the HMI runs and vanish on reboot.

| # | Rung | How to check | Proves |
|---|---|---|---|
| 1 | **Object loaded** | A `__attribute__((constructor))` in your `.so` writes `/tmp/<name>_loaded` on `dlopen`; `ls -l` it | Discovery + `dlopen` succeeded — an **unsigned, uncoded** object in `Plugins/` was mapped |
| 2 | **ABI accepted** | Your `create()` writes `/tmp/<name>_created`; `ls -l` it | The loader found and called through `pluginAppInfo` — descriptor layout and `create` signature are right |
| 3 | **Framework logs** | `sloginfo \| grep -i <name>` | The framework's own view — integration messages or errors about your plugin |
| 4 | **Menu entry appears** | Look for your entry in the HMI menu declared by your DescFile | The DescFile parsed and the app integrated into the menu tree |

Concretely (reference plugin markers; substitute your own paths):

```sh
ls -l /tmp/diag_plugin_loaded    # rung 1: constructor fired  -> load proven
ls -l /tmp/diag_plugin_created   # rung 2: create() called    -> ABI accepted
sloginfo | grep -i diagnostic    # rung 3: framework log lines
# rung 4: a "PowerTools"/Diagnostics entry shows up in the menu (from the DescFile)
```

Rung 1 is the important one to instrument first: it fires *the instant* the object is
`dlopen`'d, **independent of any `bmw::` ABI correctness** (`diagnostics.cpp:19-22`).
Because the reference object carries **no `.p7b`/`.p12`** and lives in the uncoded
`Plugins/` dir, rung 1 passing is what proves that discovery + an **unsigned, uncoded**
object are accepted. This is not stock-unit-untested anymore: the load path links no
cryptography and has no signature branch (`01 §3.1`), and the owner's own unsigned plugin
loaded from `Plugins/` on a stock unit. OPT_DEBUG only grants the *filesystem write* to
place the files; it does not change the load gate.

If rung 1 passes but rung 2 fails, the object loaded but your `pluginAppInfo` is wrong (bad
`create` pointer, wrong descriptor layout, mangled symbol — compare against the §3 checks).
If rung 1 itself fails, the file isn't being discovered: re-check the directory
(`Plugins/`, not `PluginsCoded/`), the `lib<Name>.so` filename vs the manifest `<file>`
base name, that you wrote under the correct writable mount (§4.2), and that you actually
restarted the HMI.

A minimal marker helper you can paste into any plugin:

```cpp
#include <cstdio>
#include <unistd.h>
#include <ctime>

static void marker(const char* path, const char* what) {
    FILE* f = fopen(path, "w");
    if (f) { fprintf(f, "%s pid=%d time=%ld\n", what, (int)getpid(), (long)time(0)); fclose(f); }
}

__attribute__((constructor))
static void on_load() { marker("/tmp/myplugin_loaded", "libMyPlugin.so dlopened"); }
// ...and call marker("/tmp/myplugin_created", ...) as the first line of your create().
```

---

## 7. Rollback

Deployment is **fully reversible** because a plugin is nothing but loose files in a
directory — the HMI binary is never modified. To remove a plugin, delete its directory and
restart the HMI (`DEPLOY.md`, Rollback). Remove it from the **same writable mount point**
you deployed to:

```sh
# On the HU, as root. Same mount point as the deploy (reference unit: /fs/sda0).
mount -uw /fs/sda0
rm -rf /fs/sda0/opt/hmi/ID5/data/ro/Plugins/MyPlugin
sync
# restart HmiMain3D (or reboot)
```

After the restart the scan finds nothing in that slot and the unit is byte-for-byte back
to where it was. This reversibility is the whole reason the loose-file `Plugins/` path is
the right place to develop: a broken plugin costs you a directory delete and a restart, not
a reflash.

---

## 8. End-to-end checklist

1. `source qnx650/env.sh` → `ntoarm-g++` (gcc 4.4.2) on `PATH`.
2. Point the Makefile `CARVE` at your own carved `libAppFramework.A.so` + `libCoreFramework.A.so`.
3. `make` → `lib<Name>.so`.
4. Self-check: `file` (ARM 32-bit), `readelf -A` (EABI attrs match the framework), `nm -DC | grep pluginAppInfo` (exported, 24-byte OBJECT), `nm -DCu | grep bmw` (undefined refs present).
5. On the HU as root: `mount -uw <data-partition>`, `mkdir` the `Plugins/<Name>` dir **under that mount point**, copy the three files, `sync`.
6. Restart `HmiMain3D` (or reboot).
7. Walk the validation ladder: `_loaded` → `_created` → `sloginfo` → menu entry.
8. Iterate; `rm -rf` the dir under the same mount + restart to roll back at any point.

---

*Cross-references: the `pluginAppInfo`/`PluginApp` ABI and the 34-slot vtable are covered
in the ABI doc; the `.manifest` schema (`type`, `autoStart`, `dependencies`,
`{pluginDir}`, `DescFile`) in the manifest doc; the DescFile (`hmiState`/component/action/
model) grammar in the DescFile/XML doc.*

---

## Sources

These facts were reverse-engineered from an **owner-authorized offline flash carve** of
the author's own titled vehicle plus **on-car validation** on that same unit. Nothing here
requires access to a network or a vehicle you do not own.

- **Toolchain / build:** framework `.comment` = `GCC: (GNU) 4.4.2` (`readelf -p .comment`
  on `libAppFramework.A.so`, `libCoreFramework.A.so`); QNX SDP 6.5.0 `env.sh`; compile/link
  flags `capabilities/plugins/reference/example-plugin/Makefile`.
- **Framework symbols (both libs required):** `nm -DC` on
  `.../opt/hmi/ID5/lib/libAppFramework.A.so` (`PluginApp` ctor `_ZN3bmw9PluginAppC1E...`
  @0x6f80, `updateModel` @0x539c, `setProperty` @0x54a4, `addHandler` @0x5970/0x5db0,
  `post` @0x6024) and `libCoreFramework.A.so` (`DataTableBase::DataTableBase` @0xaa24,
  `::clear` @0xaa90, `Variant::operator=` @0x9d04).
- **Entry point / loader:** `file`, `nm -DC`, `readelf -sW`, `nm -DCu` on
  `libDiagnostics.so`; `strings HmiMain3D` → the two `pluginAppInfo` error strings and the
  `/Plugins`, `/Plugins/`, `/PluginsCoded` path stems.
- **Layout / naming / signing:** `Diagnostics.manifest:5,16`; OEM
  `SecurityMenu.manifest:5,16-22`; `.p7b`/`.p12` present in
  `.../PluginsCoded/{SecurityMenu,ActiveSeating}/`; the distinct out-of-scope
  `.../hmiplugins/{A4APlugin.xml,RemotingPlugin.xml}` bundles.
- **Deploy / discovery / rollback:** `capabilities/plugins/docs/08-building-and-deploying.md` (all
  paths under `/fs/sda0/opt/hmi/ID5/data/ro/Plugins/...`); marker mechanics
  `diagnostics.cpp:14-40`.
- **Shell precondition:** the OPT_DEBUG dev surface — [`../../flash_and_patching/`](../../flash_and_patching/) and [`../../../docs/staging-files-over-ssh.md`](../../../docs/staging-files-over-ssh.md).

**Reconstructed-ABI notice.** The `bmw_abi.h` / `bmw_list.h` headers are **hand-reconstructed**
from stripped framework libraries and the `HmiMain3D` binary (`bmw_abi.h:1-3`,
`bmw_list.h:1-5`). They are correct enough that a real plugin loads, constructs, and runs,
but they are **not** OEM headers: struct sizes are deliberately over-padded and only the
fields/vtable slots a plugin touches are modeled. Claims tagged **RECONSTRUCTED** above
(the `pluginAppInfo` descriptor layout, the `abiVersion` major/minor interpretation) rest
on those headers; claims tagged **VERIFIED** are carve- or on-car-confirmed. Whether a
fully-stock (non-OPT_DEBUG) unit loads an unsigned object from `Plugins/` at all is
genuinely **open** — the successful loads reported here were observed on a unit already in
the OPT_DEBUG state.
