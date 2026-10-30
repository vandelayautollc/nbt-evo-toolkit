// diagnostics.cpp — the reference NBT-Evo HMI plugin: DTC tool + SVT master-detail tool.
//
// The plugin menu (state 100) has two items:
//   "Read DTCs" -> DTC tool (state 200): "Build module list" (raAction 21) then
//        "Read DTCs" (raAction 22, greyed until modules built). Reads confirmed/
//        active/pending DTCs per module, filling in "[Status] NNNNNN" incrementally.
//   "SVT"       -> SVT tool (state 300): "Read SVT" (raAction 24). Discovers live
//        modules and reads each one's installed software (SVK, UDS 22 F1 01) via
//        dtc_scan --svt-out /tmp/pt_svt.txt. SPLIT LAYOUT: the left list (model 51,
//        raAction 25) shows a "Vehicle Info" entry + one row per module; selecting a
//        row fills the RIGHT list (model 52) with that group's detail (VIN/I-Stufe for
//        Vehicle Info, or the module's "CLASS ID VER" SVK parts). The results file is
//        group-structured: a non-indented line = a left-list row (group header); the
//        indented lines under it = that group's detail.
//
// Safety (unchanged proven design): every scan is an isolated child (posix_spawn);
// the UI thread never blocks; a self-rescheduling Runnable polls waitpid(WNOHANG)
// ON THE UI THREAD (post, ms) and does all model/property updates there.
// setProperty(comp, SELECTABLE=2, Parcel(bool)) greys/un-greys the buttons.
#include "bmw_list.h"
#include <cstdio>
#include <cstring>
#include <spawn.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>

extern char **environ;

static const char *SCAN_BIN = "/fs/sda0/opt/hmi/ID5/data/ro/Plugins/Diagnostics/dtc_scan";
static const char *GW       = "169.254.104.13";     // this car's FEM gateway (DIAGADR10)
static const char *MODS     = "/tmp/pt_modules.txt"; // DTC module list ("0xNN NAME")
static const char *RES      = "/tmp/pt_results.txt"; // incremental DTC results
static const char *SVT_RES  = "/tmp/pt_svt.txt";     // incremental SVT results

enum {
    BUILD_BTN       = 3,   // component ids (setProperty targets)
    READ_BTN        = 4,
    SVTREAD_BTN     = 8,
    PROP_SELECTABLE = 2,
    LIST_MODEL      = 50,  // DTC list model
    SVT_LIST_MODEL  = 51,  // SVT left list model (group headers)
    SVT_DETAIL_MODEL= 52,  // SVT right list model (selected group's detail)
    BUILD_ACTION    = 21,  // raAction ids
    READ_ACTION     = 22,
    ROW_ACTION      = 23,
    SVT_ACTION      = 24,
    SVTROW_ACTION   = 25,
    REREAD_ACTION   = 26,  // OPTION menu (DTC screen): "Re-read DTCs"
    CLEARDTC_ACTION = 27,  // OPTION menu (DTC screen): "Clear DTCs"
    KIND_BUILD      = 0,
    KIND_READ       = 1,
    KIND_SVT        = 2
};

static void dlog(const char *s){ FILE*f=fopen("/tmp/diag_trace.log","a"); if(f){fputs(s,f);fputc('\n',f);fclose(f);} }
static void dlogf(const char *fmt,long v){ char b[160]; snprintf(b,sizeof b,fmt,v); dlog(b); }

static long file_size(const char* p){ FILE*f=fopen(p,"rb"); if(!f)return -1; fseek(f,0,SEEK_END); long s=ftell(f); fclose(f); return s; }
static bool file_nonempty(const char* p){ return file_size(p) > 0; }

__attribute__((constructor)) static void mk(void){ dlog("[so] loaded v12-svt-richtext-detail"); }

class Diagnostics;   // fwd

// Self-rescheduling UI-thread poller for the scan child.
class ChildPoller : public bmw::Runnable {
public:
    ChildPoller(Diagnostics* app, pid_t pid, unsigned ms) : app_(app), pid_(pid), ms_(ms) {}
    virtual ~ChildPoller() {}
    virtual void run();
private:
    Diagnostics* app_; pid_t pid_; unsigned ms_;
};

class Diagnostics : public bmw::PluginApp {
public:
    Diagnostics(bmw::IDispatcher& d, bmw::BasicString<char> name, unsigned maj, unsigned mn,
                bmw::RHMIInterfaceVersion rhmi, const bmw::Bundle& cfg, const bmw::Bundle& res)
        : bmw::PluginApp(d,name,maj,mn,rhmi,cfg,res),
          scanning_(false), scan_kind_(0), modules_built_(false), pid_(0), last_res_size_(-1),
          selected_svt_(0), ngroups_(0) {}

    virtual bool onInit();
    virtual bool onFinalize();
    bool onBuild  (const bmw::Parcel&);   // raAction 21
    bool onRead   (const bmw::Parcel&);   // raAction 22
    bool onRow    (const bmw::Parcel&);   // raAction 23
    bool onReadSvt(const bmw::Parcel&);   // raAction 24
    bool onSvtRow (const bmw::Parcel&);   // raAction 25
    bool onReReadDtc(const bmw::Parcel&); // raAction 26 (OPTION: Re-read DTCs)
    bool onClearDtc (const bmw::Parcel&); // raAction 27 (OPTION: Clear DTCs)

    void fill(unsigned model, const char* path, const char* hint);
    void refresh_dtc();                      // DTC list from RES (else MODS, else hint)
    void refresh_svt();                      // SVT master-detail: left + right
    void fill_svt_left();                    // SVT left list (group headers) from SVT_RES
    void fill_svt_right();                   // SVT right list (selected group's detail)
    void set_button(unsigned comp, bool en); // gray / un-gray via SELECTABLE
    void spawn_and_poll(int kind, char* const argv[]);
    void on_poll_running();                  // per-tick: refresh if active results file grew
    void on_scan_done();                     // finalize a scan

    bool  scanning_;
    int   scan_kind_;
    bool  modules_built_;
    pid_t pid_;
    long  last_res_size_;
    int   selected_svt_;   // which SVT left-list group is selected (0 = Vehicle Info)
    int   ngroups_;        // number of SVT left-list groups (for clamping selection)
};

static void add_row(bmw::DataTable<1>& t, unsigned r, const char* s){
    bmw::Variant& c = t.at(r,0);
    c.m_impl = new bmw::Variant::ObjectContainer<bmw::BasicString<char> >(bmw::BasicString<char>(s));
}

void Diagnostics::fill(unsigned model, const char* path, const char* hint){
    bmw::DataTable<1>* t = new bmw::DataTable<1>();   // deep-copied by updateModel
    unsigned n = 0;
    if (path && file_nonempty(path)){
        FILE* f = fopen(path, "r");
        if (f){
            char buf[256];
            while (n < 400 && fgets(buf, sizeof buf, f)){
                int L = (int)strlen(buf);
                while (L>0 && (buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
                if (L==0) continue;
                add_row(*t, n++, buf);
            }
            fclose(f);
        }
    }
    if (n == 0) add_row(*t, n++, scanning_ ? "Working..." : hint);
    updateModel(model, *t);
    dlogf("[app] fill rows=%ld", (long)n);
}

void Diagnostics::refresh_dtc(){
    const char* path = 0;
    if (file_nonempty(RES))       path = RES;
    else if (file_nonempty(MODS)) path = MODS;
    fill((unsigned)LIST_MODEL, path, "Press \"Build module list\"");
}

// A results line that does NOT start with whitespace is a GROUP HEADER (left-list
// row); indented lines under it are that group's DETAIL (right-list rows).
void Diagnostics::fill_svt_left(){
    bmw::DataTable<1>* t = new bmw::DataTable<1>();
    unsigned n = 0;
    FILE* f = fopen(SVT_RES, "r");
    if (f){
        char buf[256];
        while (n < 400 && fgets(buf, sizeof buf, f)){
            if (buf[0]==' ' || buf[0]=='\t') continue;      // detail line -> skip
            int L=(int)strlen(buf); while(L>0&&(buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
            if (L==0) continue;
            add_row(*t, n++, buf);
        }
        fclose(f);
    }
    ngroups_ = (int)n;
    if (n == 0) add_row(*t, n++, scanning_ ? "Working..." : "Press \"Read SVT\"");
    updateModel((unsigned)SVT_LIST_MODEL, *t);
}

// Right pane = a Richtext LABEL (model 52), not a list: labels aren't focusable
// (no stray scroll target) and text lines stack (no overlap). Build ONE string =
// the selected group's detail lines joined by '\n'.
void Diagnostics::fill_svt_right(){
    char buf[4096]; int off = 0; buf[0] = 0;
    FILE* f = fopen(SVT_RES, "r");
    if (f){
        char line[256]; int grp = -1;
        while (fgets(line, sizeof line, f)){
            bool hdr = !(line[0]==' ' || line[0]=='\t');
            if (hdr){ grp++; continue; }
            if (grp == selected_svt_){                       // detail of the selected group
                int L=(int)strlen(line); while(L>0&&(line[L-1]=='\n'||line[L-1]=='\r')) line[--L]=0;
                char* s = line; while(*s==' ') s++;          // strip indent for the pane
                if (*s){ int w = snprintf(buf+off, sizeof buf-off, "%s\n", s);
                         if (w > 0 && off + w < (int)sizeof buf) off += w; else break; }
            }
        }
        fclose(f);
    }
    if (off == 0) snprintf(buf, sizeof buf, "%s", scanning_ ? "Reading..." : "");
    updateModel((unsigned)SVT_DETAIL_MODEL, bmw::BasicString<char>(buf));
    dlogf("[app] svt right sel=%ld", (long)selected_svt_);
}

void Diagnostics::refresh_svt(){ fill_svt_left(); fill_svt_right(); }

void Diagnostics::set_button(unsigned comp, bool en){
    bmw::Parcel p(en);
    setProperty(comp, (unsigned)PROP_SELECTABLE, p);
}

void Diagnostics::spawn_and_poll(int kind, char* const argv[]){
    if (scanning_) return;
    posix_spawn_file_actions_t fa;
    posix_spawn_file_actions_init(&fa);
    posix_spawn_file_actions_addopen(&fa, 0, "/dev/null", O_RDONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 1, "/dev/null", O_WRONLY, 0);
    posix_spawn_file_actions_addopen(&fa, 2, "/dev/null", O_WRONLY, 0);
    pid_t pid = 0;
    int rc = posix_spawn(&pid, SCAN_BIN, &fa, 0, argv, environ);
    posix_spawn_file_actions_destroy(&fa);
    if (rc != 0){ dlogf("[app] posix_spawn rc=%ld", (long)rc); return; }
    scanning_ = true; scan_kind_ = kind; pid_ = pid; last_res_size_ = -1;
    if (kind == KIND_SVT){
        set_button((unsigned)SVTREAD_BTN, false);
        refresh_svt();
    } else {
        set_button((unsigned)BUILD_BTN, false);
        if (kind == KIND_READ) set_button((unsigned)READ_BTN, false);
        refresh_dtc();
    }
    post(new ChildPoller(this, pid, 400u), 400u);
    dlogf("[app] scan started pid=%ld", (long)pid);
}

bool Diagnostics::onBuild(const bmw::Parcel&){
    dlog("[app] onBuild");
    if (scanning_) return true;
    remove(RES);                              // drop stale DTC results
    modules_built_ = false;
    set_button((unsigned)READ_BTN, false);    // keep "Read DTCs" greyed during build
    char* argv[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--enum-out", (char*)MODS, 0 };
    spawn_and_poll(KIND_BUILD, argv);
    return true;
}

bool Diagnostics::onRead(const bmw::Parcel&){
    dlog("[app] onRead");
    if (scanning_ || !modules_built_) return true;
    char* argv[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--read-modules", (char*)MODS,
                     (char*)"--live-out", (char*)RES, (char*)"--timeout", (char*)"3", 0 };
    spawn_and_poll(KIND_READ, argv);
    return true;
}

bool Diagnostics::onReadSvt(const bmw::Parcel&){
    dlog("[app] onReadSvt");
    if (scanning_) return true;
    remove(SVT_RES);                          // drop stale SVT results
    selected_svt_ = 0;                        // default selection = Vehicle Info
    char* argv[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--svt-out", (char*)SVT_RES,
                     (char*)"--timeout", (char*)"3", 0 };
    spawn_and_poll(KIND_SVT, argv);
    return true;
}

// OPTION-menu actions on the DTC screen. Whole-car (RHMI gives no hover/focus, so we
// can't scope to the highlighted module yet). Use the built module list if present,
// else self-contained discover+read via --scan-out. Both fill the DTC list (model 50).
bool Diagnostics::onReReadDtc(const bmw::Parcel&){
    dlog("[app] onReReadDtc");
    if (scanning_) return true;
    remove(RES);
    if (modules_built_){
        char* a[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--read-modules", (char*)MODS,
                      (char*)"--live-out", (char*)RES, (char*)"--timeout", (char*)"3", 0 };
        spawn_and_poll(KIND_READ, a);
    } else {
        char* a[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--scan-out", (char*)RES,
                      (char*)"--timeout", (char*)"3", 0 };
        spawn_and_poll(KIND_READ, a);
    }
    return true;
}

bool Diagnostics::onClearDtc(const bmw::Parcel&){
    dlog("[app] onClearDtc");
    if (scanning_) return true;
    remove(RES);
    if (modules_built_){
        char* a[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--read-modules", (char*)MODS,
                      (char*)"--live-out", (char*)RES, (char*)"--clear", (char*)"--timeout", (char*)"3", 0 };
        spawn_and_poll(KIND_READ, a);
    } else {
        char* a[] = { (char*)SCAN_BIN, (char*)GW, (char*)"--scan-out", (char*)RES,
                      (char*)"--clear", (char*)"--timeout", (char*)"3", 0 };
        spawn_and_poll(KIND_READ, a);
    }
    return true;
}

bool Diagnostics::onRow (const bmw::Parcel& p){ int i=-1; p.readInt32(i); (void)i; dlog("[app] onRow"); return true; }
bool Diagnostics::onSvtRow(const bmw::Parcel& p){
    int i = -1;
    if (!p.readInt32(i)){ unsigned u=0; if (p.readUInt32(u)) i=(int)u; }
    dlogf("[app] onSvtRow idx=%ld", (long)i);
    if (i >= 0 && i < ngroups_){ selected_svt_ = i; fill_svt_right(); }  // update right pane
    return true;
}

void Diagnostics::on_poll_running(){
    long sz;
    if (scan_kind_ == KIND_SVT)       sz = file_size(SVT_RES);
    else if (scan_kind_ == KIND_READ) sz = file_size(RES);
    else return;                                            // BUILD: no incremental fill
    if (sz != last_res_size_){
        last_res_size_ = sz;
        if (scan_kind_ == KIND_SVT) refresh_svt(); else refresh_dtc();
    }
}

void Diagnostics::on_scan_done(){
    scanning_ = false;
    if (scan_kind_ == KIND_SVT){
        refresh_svt();
        set_button((unsigned)SVTREAD_BTN, true);
    } else {
        if (scan_kind_ == KIND_BUILD) modules_built_ = file_nonempty(MODS);
        refresh_dtc();
        set_button((unsigned)BUILD_BTN, true);
        set_button((unsigned)READ_BTN, modules_built_);
    }
    dlogf("[app] scan done kind=%ld", (long)scan_kind_);
}

bool Diagnostics::onInit(){
    dlog("[app] onInit");
    refresh_dtc();                            // DTC hint (no scan on boot)
    refresh_svt();                            // SVT hint
    bmw::Delegate<bool, const bmw::Parcel&> dB; dB.m_obj=this;
    dB.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onBuild>;
    addHandler((unsigned)BUILD_ACTION, dB);
    bmw::Delegate<bool, const bmw::Parcel&> dR; dR.m_obj=this;
    dR.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onRead>;
    addHandler((unsigned)READ_ACTION, dR);
    bmw::Delegate<bool, const bmw::Parcel&> dW; dW.m_obj=this;
    dW.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onRow>;
    addHandler((unsigned)ROW_ACTION, dW);
    bmw::Delegate<bool, const bmw::Parcel&> dS; dS.m_obj=this;
    dS.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onReadSvt>;
    addHandler((unsigned)SVT_ACTION, dS);
    bmw::Delegate<bool, const bmw::Parcel&> dV; dV.m_obj=this;
    dV.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onSvtRow>;
    addHandler((unsigned)SVTROW_ACTION, dV);
    bmw::Delegate<bool, const bmw::Parcel&> dRR; dRR.m_obj=this;
    dRR.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onReReadDtc>;
    addHandler((unsigned)REREAD_ACTION, dRR);
    bmw::Delegate<bool, const bmw::Parcel&> dCL; dCL.m_obj=this;
    dCL.m_exec=&bmw::Delegate<bool,const bmw::Parcel&>::execImpl<Diagnostics,&Diagnostics::onClearDtc>;
    addHandler((unsigned)CLEARDTC_ACTION, dCL);
    return true;
}
bool Diagnostics::onFinalize(){ return true; }

void ChildPoller::run(){
    int st = 0;
    pid_t r = ::waitpid(pid_, &st, WNOHANG);
    if (r == 0){ app_->on_poll_running(); app_->post(this, ms_); return; }  // running -> repost
    app_->on_scan_done();
    delete this;                                                            // done -> free (last)
}

struct PluginAppInfo {
    unsigned int abiVersion; const char* name; const char* vendor; unsigned int ifaceVersion;
    bmw::PluginApp* (*create)(bmw::IDispatcher&, const char*, const bmw::Bundle&, const bmw::Bundle&);
    void (*destroy)(bmw::PluginApp*);
};
static bmw::PluginApp* diag_create(bmw::IDispatcher& d, const char* nm, const bmw::Bundle& c, const bmw::Bundle& r){
    bmw::RHMIInterfaceVersion v; v.value = 1;
    return new Diagnostics(d, bmw::BasicString<char>(nm), 1u, 0u, v, c, r);
}
static void diag_destroy(bmw::PluginApp* a){ delete a; }
extern "C" PluginAppInfo pluginAppInfo = {
    1, "Diagnostics", "owner-research", 1, diag_create, diag_destroy
};
