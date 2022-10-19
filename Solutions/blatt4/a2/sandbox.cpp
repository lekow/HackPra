#include <iostream>
#include <fstream>
#include <dlfcn.h>
#include <string.h>
#include <vector>
using namespace std;

// original fopen function
FILE* (*fopen_org)(const char*, const char*);
// our helper functions for checking blacklisted files
vector<string> readBlacklist();
bool isBlacklisted(const char*);

// read the blacklist and save it into a vector
vector<string> blacklist = readBlacklist();

FILE* fopen(const char *filename, const char *mode) {
    // load the dynamic library libc.so.6 (lazy binding)
    void *handle = dlopen("/lib/x86_64-linux-gnu/libc.so.6", RTLD_LAZY);
    // get the original fopen function and save it for later use
    fopen_org = (FILE*(*)(const char*, const char*)) dlsym(handle, "fopen");

    // check if the filename (basename only) that needs to be accessed is blacklisted
    if (isBlacklisted(basename(filename)))
        return NULL;

    // if the filename is not blacklisted, return the result from the original fopen function
    return fopen_org(filename, mode);
}

// read the blacklisted files line by line from blacklist.lst and save them in a vector
vector<string> readBlacklist() {
    vector<string> blacklist;
    string line;
    ifstream in("blacklist.lst");

    while (getline(in, line))
        blacklist.push_back(line);

    return blacklist;
}

// iterate over all strings from the vector and compare them to the given filename (basename only)
bool isBlacklisted(const char *filename) {
    for (int i = 0; i < blacklist.size(); i++) {
        if (strcmp(filename, blacklist[i].c_str()) == 0)
            return true;
    }

    return false;
}
