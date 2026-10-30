// diagnostics.cpp — Stage-1 loader-validation plugin for the NBT-Evo HMI.
// Goal: prove an UNSIGNED, UN-CODED plugin dropped in data/ro/Plugins/ is
// discovered, dlopen'd and constructed by HmiMain3D — with zero risk to the HMI.
//
// Signals (readable over ssh while the HMI runs; /tmp is RAM):
//   /tmp/diag_plugin_loaded   -> written by a .so constructor (fires on dlopen)  == discovery+load proven
//   /tmp/diag_plugin_created  -> written when the framework calls our create()   == descriptor/ABI accepted
// Plus the "Diagnostics" menu entry (declared in Diagnostics.xml) should appear.
#include "bmw_abi.h"
#include <cstdio>
#include <unistd.h>
#include <ctime>

static void marker(const char* path, const char* what) {
    FILE* f = fopen(path, "w");
    if (f) { fprintf(f, "%s pid=%d time=%ld\n", what, (int)getpid(), (long)time(0)); fclose(f); }
}

// Fires the instant HmiMain3D dlopen()s this .so — the definitive load proof,
// independent of any bmw:: ABI correctness.
__attribute__((constructor))
static void diag_on_load() { marker("/tmp/diag_plugin_loaded", "libDiagnostics.so dlopened"); }

// The framework calls this to instantiate the plugin app. We return a real
// bmw::PluginApp (its ctor installs the real vtable), so subsequent virtual
// calls dispatch into libAppFramework — no crash, default (empty) behaviour.
static bmw::IPluginApp* diag_create(bmw::IDispatcher& disp, const char* name,
                                    const bmw::Bundle& cfg, const bmw::Bundle& res) {
    marker("/tmp/diag_plugin_created", "Diagnostics::create called");
    bmw::RHMIInterfaceVersion rhmi; rhmi.value = 1;          // == pluginAppInfo.ifaceVersion
    bmw::PluginApp* p =
        new bmw::PluginApp(disp, bmw::BasicString<char>(name),
                           1u /*major*/, 0u /*minor*/, rhmi, cfg, res);
    return reinterpret_cast<bmw::IPluginApp*>(p);            // IPluginApp = primary base @off 0
}

static void diag_destroy(bmw::IPluginApp* app) {
    marker("/tmp/diag_plugin_destroyed", "Diagnostics::destroy called");
    (void)app;   // stage-1: intentionally leak (proper dtor is stage-2)
}

// Exported, un-mangled symbol the loader dlsym()s.
extern "C" PluginAppInfo pluginAppInfo = {
    1,                 // abiVersion  (ctor: major=1, minor=0)
    "Diagnostics",     // name
    "owner-research",  // vendor
    1,                 // ifaceVersion (ctor: RHMIInterfaceVersion=1)
    diag_create,
    diag_destroy,
};
