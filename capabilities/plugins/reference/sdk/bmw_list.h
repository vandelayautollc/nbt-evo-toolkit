// bmw_list.h - reconstructed BMW NBT-Evo HMI plugin SDK subset (list-capable).
// Layouts/tags recovered from libAppFramework.A.so, libCoreFramework.A.so,
// libSecurityMenu.so and HmiMain3D. Real method bodies live in the shared libs
// (resolved at link/dlopen). We only reconstruct data layouts + inline templates
// (Variant/ObjectContainer/Map/Delegate/DataTable) that the OEM ships header-only.
#ifndef BMW_LIST_H
#define BMW_LIST_H
#include <string>   // for std::string (getCapabilities mangling: RKSs)

namespace bmw {

class IDispatcher; class Bundle; class Message;

// --- Runnable: ROOT interface, sizeof 4 (vptr only). vtable = [~D1, ~D0, run()].
//     Subclass and override run(); post it via PluginApp::post(Runnable*[, ms]) and
//     run() fires on the HMI dispatcher (UI) thread. Framework never frees it: a
//     one-shot must `delete this` at the END of run(); a rescheduling one reposts
//     (post(this,ms)) and returns without deleting. ~Runnable() resolves from lib.
class Runnable {
public:
    // Inline (empty) dtor ON PURPOSE: a derived Runnable's dtor calls the base
    // *base-object* dtor _ZN3bmw8RunnableD2Ev, which the OEM libs DO NOT export
    // (only D1/D0). Defining it here emits a local weak D2/D1/D0 so dlopen(RTLD_NOW)
    // resolves. vtable/typeinfo become COMDAT-weak and merge with the libs' copies.
    virtual ~Runnable() {}        // emits local weak _ZN3bmw8RunnableD2Ev/D1Ev/D0Ev
    virtual void run() = 0;       // vtable slot 2
};
namespace ResourceType { enum ResourceTypes { RESOURCE_TYPE_DUMMY = 0 }; }

// --- BasicString<T>: 4 bytes = single COW pointer; non-trivial (link real methods)
template <class T>
class BasicString {
    T* m_data;                                   // +0 (COW buffer ptr; header at [-12..-1])
public:
    BasicString(const T* s);                     // _ZN3bmw11BasicStringIcEC1EPKc
    BasicString(const BasicString& o);           // _ZN3bmw11BasicStringIcEC1ERKS1_
    ~BasicString();                              // _ZN3bmw11BasicStringIcED1Ev
    BasicString& operator=(const BasicString&);  // _ZN3bmw11BasicStringIcEaSERKS1_
};

// --- 4-byte POD passed by value
struct RHMIInterfaceVersion { unsigned int value; };

// --- TextID: 8 bytes, trivially copyable, ctor(uint)  (_ZN3bmw6TextIDC1Ej)
class TextID { unsigned int m_a, m_b; public: TextID(unsigned int id); };

// --- Parcel: a serialization buffer. REAL layout (from RE) = 20 bytes, 4-aligned:
//     {buf*@0, size@4, cap@8, vptr@12, pos@16}; the ctor fills all of it (incl. the
//     vptr) and ~Parcel frees buf@0. We store 20 bytes of 4-aligned raw and let the
//     real ctor/dtor (linked) manage it -- do NOT declare virtuals here (the real
//     vptr lives at +12, not +0). Copy/assign hidden (would shallow-copy buf@0).
class Parcel {
    unsigned int _raw[5];                    // 20 bytes, 4-byte aligned
public:
    Parcel();                                // _ZN3bmw6ParcelC1Ev
    explicit Parcel(bool);                   // _ZN3bmw6ParcelC1Eb  (value written via writeBool)
    ~Parcel();                               // _ZN3bmw6ParcelD1Ev
    bool readInt32 (int&)          const;    // _ZNK3bmw6Parcel9readInt32ERi
    bool readUInt32(unsigned int&) const;    // _ZNK3bmw6Parcel10readUInt32ERj
    bool readBool  (bool&)         const;    // _ZNK3bmw6Parcel8readBoolERb
private:
    Parcel(const Parcel&);                   // undefined on purpose (avoid shallow copy)
    Parcel& operator=(const Parcel&);
};

// --- Variant type tags (from ObjectContainer<T>::type() constants)
template <class T> struct VariantTag;                                   // primary (undefined)
template <> struct VariantTag< BasicString<char> > { enum { value = 34 }; };  // 0x22
template <> struct VariantTag< TextID >            { enum { value = 40 }; };  // 0x28

// --- Variant handle (4 bytes) + polymorphic pimpl container (header-only template)
class Variant {
public:
    class IObjectContainer {                     // vtable: [0]~D1 [1]~D0 [2]type [3]clone
    public:
        virtual ~IObjectContainer();
        virtual unsigned int type()   const = 0;
        virtual IObjectContainer* clone() const = 0;
    };
    template <class T>
    class ObjectContainer : public IObjectContainer {
    public:
        T m_val;                                 // +4 (payload; as<T>() returns this+4)
        ObjectContainer(const T& v) : m_val(v) {}
        virtual ~ObjectContainer() {}
        virtual unsigned int type() const { return (unsigned int)VariantTag<T>::value; }
        virtual IObjectContainer* clone() const { return new ObjectContainer<T>(m_val); }
    };
    IObjectContainer* m_impl;                    // +0
};
inline Variant::IObjectContainer::~IObjectContainer() {}

// --- Map<K,V>: reconstructed for Map<uint,Variant> (24 bytes). ctor sets the exact
//     default fields the OEM inlines; at()/operator[] (libCoreFramework) manage the rest.
template <class K, class V>
class Map {
    void*        m_buckets;      // +0  buckets ptr           = 0
    unsigned int m_bucketCount;  // +4  hash modulus          = 17  (MUST be nonzero)
    unsigned int m_size;         // +8  entry count           = 0
    unsigned int m_f12;          // +12                        = 0
    void*        m_memBlock;     // +16 node pool             = 0
    unsigned int m_f20;          // +20 nodes-per-pool-chunk  = 10
public:
    Map() : m_buckets(0), m_bucketCount(17), m_size(0),
            m_f12(0), m_memBlock(0), m_f20(10) {}
    // Read-only lookup of a uint key, as the OEM's inline Map<uint,Variant>::lookup (libActiveSeating.so 0xcd00):
    // bucket = ror(key, 4) % m_bucketCount; each node is {next @+0, ? @+4, key @+8, value @+12}. Returns the stored
    // value, or 0. For reading a map the HMI hands a handler; the map must outlive the returned pointer.
    const V* find(unsigned int key) const {
        if (!m_buckets || !m_bucketCount) return 0;
        const unsigned int* node =
            static_cast<const unsigned int* const*>(m_buckets)[rem((key >> 4) | (key << 28), m_bucketCount)];
        for (; node; node = reinterpret_cast<const unsigned int*>(node[0]))
            if (node[2] == key) return reinterpret_cast<const V*>(node + 3);
        return 0;
    }
private:
    // n % d by long division. The plugin toolchain (g++ 4.4.2) makes `%` a call to __umodsi3, which the head unit's
    // libc doesn't export, so a plugin that used it would fail to load. d must be below 2^31.
    static unsigned int rem(unsigned int n, unsigned int d) {
        unsigned int r = 0;
        for (int i = 31; i >= 0; --i) {
            r = (r << 1) | ((n >> i) & 1u);
            if (r >= d) r -= d;
        }
        return r;
    }
};

// --- DataTableBase: 8 bytes; ctor/at/clear are real exports (libCoreFramework)
class DataTableBase {
    Map<unsigned int, Variant>* m_columns;   // +0
    unsigned int                m_nColumns;  // +4
public:
    DataTableBase(Map<unsigned int, Variant>* cols, unsigned int nCols); // C1 0xaa24
    Variant& at(unsigned int row, unsigned int col) const;              // 0xab38
    void     clear();                                                    // 0xaa90
};

// --- DataTable<NCOLS>: owns the column Maps; RAII frees them via clear()
template <int NCOLS>
class DataTable : public DataTableBase {
    Map<unsigned int, Variant> m_cols[NCOLS];
public:
    DataTable() : DataTableBase(m_cols, NCOLS) {}
    ~DataTable() { clear(); }
};

// --- Delegate: 8-byte POD {obj, exec}. exec is a per-(class,method) static thunk.
template <class R, class A1 = void, class A2 = void, class A3 = void, class A4 = void>
class Delegate {
public:
    void* m_obj;                    // +0
    R (*m_exec)(void*, A1);         // +4
    template <class C, R (C::*M)(A1)>
    static R execImpl(void* self, A1 a) { return (static_cast<C*>(self)->*M)(a); }
};

// --- PluginApp: real ctor/dtor + non-virtual data methods + full 34-slot primary
//     vtable. sizeof padded to real (>=352; ctor writes up to this+348, secondary
//     PluginAppHandler vptr at +4). g++ rewrites only the primary vtable in a subclass.
class PluginApp {
    void* _vptr_primary;             // +0  (implied vptr; shown for clarity)
    char  _reserved[352 - 4];        // +4.. real fields incl. PluginAppHandler base @+4,
                                     //       m_pConnector @+88 - set by the real ctor.
public:
    PluginApp(IDispatcher& disp, BasicString<char> name,
              unsigned int major, unsigned int minor, RHMIInterfaceVersion rhmi,
              const Bundle& cfg, const Bundle& res);   // C1 0x6f80

    // non-virtual list/data setters we CALL (libAppFramework):
    void updateModel(unsigned int model, const DataTableBase& t);        // 0x539c
    void updateModel(unsigned int model, const BasicString<char>& s);    // 0x529c
    void updateModel(unsigned int model, const TextID& t);               // 0x52dc
    void addHandler (unsigned int action, const Delegate<bool, const Parcel&>& d);                 // 0x5970
    void addHandler (unsigned int state, unsigned int action, const Delegate<bool, const Parcel&>& d); // 0x5db0
    // an HMI event about one of the DescFile's states, delivered as a Map: event 1 = focus (key 4: bool focused),
    // event 11 = visibility (key 23: bool visible). OEM ActiveSeating registers both for its states (0xd7f8, 0xd81c).
    void addHandlerWithMap(unsigned int state, unsigned int event,
                           const Delegate<bool, const Map<unsigned int, Variant>&>& d);
    // set a component PROPERTY (e.g. SELECTABLE=2 -> enabled/greyed) at runtime:
    void setProperty(unsigned int component, unsigned int prop, const Parcel& value);  // _ZN3bmw9PluginApp11setPropertyEjjRKNS_6ParcelE 0x54a4
    // fire a DescFile <events> entry, e.g. a popupEvent (opens its popupHmiState). The HMI reads a Parcel(bool) as the
    // event's key-0 value: false closes the popup, true (or no value) opens it (HmiMain3D CPopupEvent::perform 0x1109380).
    // Return value, if any, unknown; unused.
    void triggerEvent(unsigned int event);                                // _ZN3bmw9PluginApp12triggerEventEj 0x5444
    void triggerEvent(unsigned int event, const Parcel& value);           // _ZN3bmw9PluginApp12triggerEventEjRKNS_6ParcelE 0x5464

    // --- 34 primary virtuals in EXACT slot order (only params/const matter for the ABI) ---
    virtual ~PluginApp();                                                  // 0,1
    virtual bool start();                                                  // 2
    virtual bool stop();                                                   // 3
    virtual bool activate();                                               // 4
    virtual bool deactivate();                                             // 5
    virtual bool init();                                                   // 6
    virtual bool finalize();                                               // 7
    virtual void post(const Message&);                                     // 8
    virtual void post(const Message&, unsigned int);                       // 9
    virtual void post(Runnable*);                                          // 10
    virtual void post(Runnable*, unsigned int);                            // 11
    virtual bool getName() const;                                          // 12
    virtual bool getResourceFile(ResourceType::ResourceTypes) const;       // 13
    virtual bool getVersion(unsigned int&, unsigned int&, unsigned int&) const; // 14
    virtual bool getRhmiVersion(RHMIInterfaceVersion&) const;              // 15
    virtual bool invokeCommand(unsigned int, const Parcel&);              // 16
    virtual bool updateModel(unsigned int, const Parcel&, unsigned char); // 17 (virtual updateModel)
    virtual bool handleEvent(unsigned int, unsigned int, const Parcel&);  // 18
    virtual bool invokeDataUpdate(unsigned int, const Parcel&);           // 19
    virtual bool requestDataValue(unsigned int);                          // 20
    virtual bool onError(unsigned int, const BasicString<char>&);         // 21
    virtual bool onInit();                                                 // 22  <-- override
    virtual bool onFinalize();                                            // 23
    virtual bool getCapabilities(const std::string&);                     // 24
    virtual bool onCheckAppAvailable();                                   // 25
    virtual bool handleMessage(const Message&);                          // 26
    virtual bool invokeCommandWithMap(unsigned int, const Map<unsigned int, Variant>&);            // 27
    virtual bool updateModelWithMap(unsigned int, const Map<unsigned int, Variant>&);              // 28
    virtual bool handleEventWithMap(unsigned int, unsigned int, const Map<unsigned int, Variant>&);// 29
    virtual bool invokeCDSUpdate(BasicString<char>&, BasicString<unsigned short>&);                // 30
    virtual bool invokeVoiceStateChanged(unsigned short);                // 31
    virtual bool invokeAppManagerUpdate(const BasicString<char>&);        // 32
    virtual bool invokeSdsEvent(unsigned int, const Map<unsigned int, Variant>&);                  // 33
};

}  // namespace bmw
#endif
