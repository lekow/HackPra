#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#define CAPITAL_SYS_CALL_NR 303


int main() {
    // the order of the variable declaration is important because of the way they are pushed onto the stack
    int proof = 0xdeadbeef;
    char out[8];
    // contains 13371337 in little-endian format
    char in[] = "aaaaaaaaaaaa\x37\x13\x37\x13\x03\x03\x03\x03";

    printf("Before syscall: proof = %x\n", proof);
    syscall(CAPITAL_SYS_CALL_NR, in, out);
    printf("After syscall: proof = %x\n", proof);

    return 0;
}
