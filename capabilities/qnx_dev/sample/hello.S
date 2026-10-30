@ Freestanding QNX Neutrino 6.5.0 / armle-v7 sample.
@ No libc, no startup objects: talks straight to the kernel-call boundary
@ the emulator models. Proves the build->emulate loop without the QNX SDP.
@   write : MsgSendv(coid=1, &iov, 1, 0, 0)   ip=0x0b
@   exit  : ThreadDestroy(tid=-1, prio=-1, status)  ip=0x2f  (tid==-1 => GuestExit)
    .arch   armv7-a
    .text
    .global _start
_start:
    ldr     r1, =iov            @ r1 = &iov (send-side descriptor)
    mov     r0, #1              @ r0 = coid = 1 (stdout)
    mov     r2, #1              @ r2 = sparts = 1
    mov     r3, #0              @ r3 = rptr = 0 (no reply)
    mov     r4, #0              @ r4 = rparts = 0
    mov     ip, #0x0b           @ __KER_MSG_SENDV
    svc     #0                  @ success -> +4, error -> +8; both fall through

    mvn     r0, #0              @ tid = -1  (all threads => process exit)
    mvn     r1, #0              @ priority = -1
    mov     r2, #0              @ status = 0
    mov     ip, #0x2f           @ __KER_THREAD_DESTROY
    svc     #0
    b       .                   @ never reached

    .data
    .align  2
msg:
    .short  0x0102              @ [0:2]  type = _IO_WRITE (_IO_BASE 0x100 + 2)
    .short  0                   @ [2:4]  combine_len
    .word   payload_end - payload   @ [4:8]  nbytes
    .word   0                   @ [8:12] xtype
    .word   0                   @ [12:16] zero
payload:
    .ascii  "hello from a hand-built QNX/ARM binary, running on our emulator\n"
payload_end:
    .align  2
iov:
    .word   msg                 @ iov[0].base
    .word   payload_end - msg   @ iov[0].len = 16-byte header + payload
