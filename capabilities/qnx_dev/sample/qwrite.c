/* Freestanding QNX Neutrino / armle-v7 in C -- no libc, no startup objects.
 * Same kernel-call boundary the emulator models. Proves the C compiler path
 * (the real HSFZ/UDS client will be C linked against the SDP's libc). */
static long k_msg_sendv(int coid, const void *siov, int sparts,
                        void *riov, int rparts) {
    register long r0 asm("r0") = coid;
    register long r1 asm("r1") = (long)siov;
    register long r2 asm("r2") = sparts;
    register long r3 asm("r3") = (long)riov;
    register long r4 asm("r4") = rparts;
    register long ip asm("ip") = 0x0b;              /* __KER_MSG_SENDV */
    asm volatile("svc #0" : "+r"(r0)
                 : "r"(r1), "r"(r2), "r"(r3), "r"(r4), "r"(ip) : "memory");
    return r0;
}
static void k_exit(int status) {
    register long r0 asm("r0") = -1;                /* tid = -1 => process */
    register long r1 asm("r1") = -1;                /* priority */
    register long r2 asm("r2") = status;
    register long ip asm("ip") = 0x2f;              /* __KER_THREAD_DESTROY */
    asm volatile("svc #0" :: "r"(r0), "r"(r1), "r"(r2), "r"(ip) : "memory");
}
struct io_write { unsigned short type, combine_len; int nbytes, xtype, zero; };
void _start(void) {
    static const char s[] = "hello from freestanding C on the QNX/ARM emulator\n";
    const int n = sizeof(s) - 1;
    struct { struct io_write h; char body[sizeof(s) - 1]; } m;
    m.h.type = 0x102; m.h.combine_len = 0; m.h.nbytes = n;
    m.h.xtype = 0; m.h.zero = 0;
    for (int i = 0; i < n; i++) m.body[i] = s[i];
    unsigned int iov[2] = { (unsigned int)(long)&m, (unsigned int)sizeof(m) };
    k_msg_sendv(1, iov, 1, 0, 0);
    k_exit(0);
}
