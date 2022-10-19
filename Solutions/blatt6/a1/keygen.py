from string import ascii_uppercase, digits
from random import randint

CHARS = [ord(c) for c in ascii_uppercase + digits]
CHARS_LEN = len(CHARS) - 1
MAX = 0x41 + 1

def main() -> None:
    key = [ord('A')] * 29
    key[5] = key[11] = key[17] = key[23] = ord('-')

    gen1(key)
    gen2(key)
    gen3(key)
    gen4(key)
    gen5(key)

    with open('license.key', 'wb') as fout:
        fout.write(bytes(key))

    print(f'License key: {"".join(chr(c) for c in key)}')

def gen1(key: list) -> None:
    key[0] = CHARS[randint(0, CHARS_LEN)]
    key[1] = CHARS[randint(0, CHARS_LEN)]
    key[2] = CHARS[randint(0, CHARS_LEN)]

    for key[3] in CHARS:
        for key[4] in CHARS:
            if key[0] ^ key[1] ^ key[2] ^ key[3] ^ key[4] == 0x41:
                return

    gen1(key)

def gen2(key: list) -> None:
    key[6] = CHARS[randint(0, CHARS_LEN)]
    key[7] = CHARS[randint(0, CHARS_LEN)]
    key[8] = CHARS[randint(0, CHARS_LEN)]
    key[10] = key[6] ^ key[7] ^ key[8]

    if key[10] not in CHARS:
        gen2(key)

def gen3(key: list) -> None:
    key[12] = CHARS[randint(0, CHARS_LEN)]
    key[13] = CHARS[randint(0, CHARS_LEN)]
    key[14] = CHARS[randint(0, CHARS_LEN)]
    key[15] = CHARS[randint(0, CHARS_LEN)]
    key[16] = key[12] & key[13] & key[14] & key[15]

    if key[16] not in CHARS:
        gen3(key)

def gen4(key: list) -> None:
    key[18] = CHARS[randint(0, CHARS_LEN)]
    key[20] = CHARS[randint(0, CHARS_LEN)]
    key[22] = CHARS[randint(0, CHARS_LEN)]

    for key[19] in CHARS:
        for key[21] in CHARS:
            if (key[18] | key[20] | key[22]) & 0xf == key[19] ^ key[21]:
                return

    gen4(key)

def gen5(key: list) -> None:
    key[24] = randint(ord('0'), ord('8'))
    key[25] = key[24] + 1
    key[26] = randint(ord('1'), ord('9'))
    key[27] = key[26] - 1
    key[28] = ord('X')

if __name__ == '__main__':
    main()
