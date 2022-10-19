#include <unistd.h>
#include <stdio.h>

#define CAPITAL_SYS_CALL_NR 303


int main() {
    char in[100] = "Hello World";
    char out[100] = "";

    syscall(CAPITAL_SYS_CALL_NR, in, out);
    printf("%s -> %s\n", in, out);

    return 0;
}
