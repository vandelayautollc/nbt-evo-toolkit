# Reference plugin

The worked RA plugin the SDK docs are built around. Two sources, same manifest/descriptor:

| File | What it is |
|---|---|
| `diagnostics.cpp` | **The reference plugin** — a DTC reader + SVT master/detail tool. The mature, safe-by-construction design (child `posix_spawn` + UI-thread `Runnable` poller + per-refresh `DataTable`) that [docs/06](../../docs/06-runtime-api-reference.md) and [docs/07](../../docs/07-threading-and-safety-model.md) reference line-by-line. Builds to `libDiagnostics.so`. |
| `hello_plugin_stage1.cpp` | The minimal **"does it even load?"** stage-1 proof: a `.so` that writes marker files from its ELF constructor (`dlopen`) and from `create()`, and nothing else. Rung 1 of the validation ladder in [docs/08](../../docs/08-building-and-deploying.md). |
| `Diagnostics.manifest`, `Diagnostics.xml` | The loader config + the DescFile (menu/screens/models) for the plugin. |
| `Makefile` | Cross-build with QNX SDP 6.5.0 (`ntoarm-g++`, gcc 4.4.2). `SRC=` selects which source. Headers come from [`../sdk`](../sdk). |

Build: source your QNX SDP env, `export NBTEVO_CARVE=…` (your own extracted HMI tree, for the two
framework `.so`s to link against), then `make` (or `make SRC=hello_plugin_stage1.cpp`). The full
procedure — deploy, discovery, the validation ladder — is in
[docs/08-building-and-deploying.md](../../docs/08-building-and-deploying.md).
