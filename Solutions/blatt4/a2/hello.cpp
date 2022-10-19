#include <iostream>
#include <fstream>
using namespace std;

int main(int argc, char *argv[]) {
    const char *filename(argv[1]);
    FILE *fout = fopen(filename, "w+");

    if (fout == NULL) {
        printf("Cannot open file '%s'!\n", filename);
        return 0;
    }

    fputs("secret\n", fout);
    fclose(fout);

    return 0;
}
