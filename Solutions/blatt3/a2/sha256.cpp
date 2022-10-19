#include <iostream>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <openssl/sha.h>
using namespace std;

int main(int argc, char *argv[]) {
    SHA256_CTX c;
    stringstream ss;
    unsigned char hash[SHA256_DIGEST_LENGTH];

    // usage: sha256 <keyLength> <messageAppend>
    if (argc != 3)
        return 0;

    // calculate the total length of the previous message (with padding and 8 bytes for length)
    // note: this number should be a multiplicative of 64; in our case: 373 + 20 + 55 = 448
    int previousLength = 373 + atoi(argv[1]) + (64 - (373 + atoi(argv[1])) % 64);
    // cast the second argument as an array of characters
    const char *messageAppend(argv[2]);

    // initialize the SHA256 algorithm
    SHA256_Init(&c);

    // change the starting size of the SHA256 algorithm to the value of previousLength
    for (int i = 0; i < previousLength; i++)
        SHA256_Update(&c, "A", 1);

    // change the initial state to 69268ba87558295eedb751d8f4744b58bd2705ce5d09984f31927bb7fbfe9b97
    c.h[0] = 0x69268ba8;
    c.h[1] = 0x7558295e;
    c.h[2] = 0xedb751d8;
    c.h[3] = 0xf4744b58;
    c.h[4] = 0xbd2705ce;
    c.h[5] = 0x5d09984f;
    c.h[6] = 0x31927bb7;
    c.h[7] = 0xfbfe9b97;

    // append our new message
    SHA256_Update(&c, messageAppend, strlen(messageAppend));
    // calculate the hmac and save it into the hash variable
    SHA256_Final(hash, &c);

    // transform the whole digest from the hash variable into a hex digest
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        ss << hex << setw(2) << setfill('0') << int(hash[i]);

    // print the new hmac
    cout << ss.str() << endl;

    return 0;
}
