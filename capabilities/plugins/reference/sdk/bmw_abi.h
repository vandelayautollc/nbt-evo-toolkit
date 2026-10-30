// bmw_abi.h — minimal hand-declared subset of the BMW NBT-Evo HMI plugin SDK
// (namespace bmw), reconstructed from libAppFramework.A.so / libSecurityMenu.so
// symbols. Just enough to construct a bmw::PluginApp and export a pluginAppInfo.
// The real class methods/ctors live in libAppFramework.A.so (resolved at dlopen).
#ifndef BMW_ABI_H
#define BMW_ABI_H

namespace bmw {

// Opaque, only ever used by reference/pointer -> incomplete decls are fine.
class IDispatcher;
class Bundle;
class IPluginApp;   // primary base of PluginApp (offset 0)

// bmw::BasicString<char> — non-trivial (user copy ctor + dtor), so g++ passes it
// by invisible reference, matching the real ABI. Size padded >= real (~24B).
template <class T>
class BasicString {
    char _opaque[32];
public:
    BasicString(const char* s);                 // _ZN3bmw11BasicStringIcEC1EPKc
    BasicString(const BasicString& o);          // _ZN3bmw11BasicStringIcEC1ERKS1_
    ~BasicString();                             // _ZN3bmw11BasicStringIcED1Ev
};

// 4-byte trivially-copyable POD -> passed by value in one word, matching the
// ctor disasm (ldr; single stack word). MUST stay trivial (no user ctor).
struct RHMIInterfaceVersion { unsigned int value; };

// bmw::PluginApp — declared opaque but correctly OVER-sized (real ~212B). We only
// need its (complete-object) ctor; the real ctor installs the real vtable, so the
// framework's virtual calls dispatch correctly without us re-declaring the vtable.
class PluginApp {
    char _opaque[512];                          // >= real sizeof(PluginApp)
public:
    PluginApp(IDispatcher& disp,
              BasicString<char> name,
              unsigned int versionMajor,
              unsigned int versionMinor,
              RHMIInterfaceVersion rhmi,
              const Bundle& cfg,
              const Bundle& res);               // _ZN3bmw9PluginAppC1E...
};

}  // namespace bmw

// The descriptor the loader dlsym()s. C linkage, exact name "pluginAppInfo".
// Layout verified from SecurityMenu/ActiveSeating (24 bytes).
struct PluginAppInfo {
    unsigned int   abiVersion;    // +0   (ctor reads low16=major, high16=minor)
    const char*    name;          // +4
    const char*    vendor;        // +8
    unsigned int   ifaceVersion;  // +12  (ctor reads this as RHMIInterfaceVersion)
    bmw::IPluginApp* (*create)(bmw::IDispatcher&, const char*,
                               const bmw::Bundle&, const bmw::Bundle&);  // +16
    void            (*destroy)(bmw::IPluginApp*);                        // +20
};

#endif
