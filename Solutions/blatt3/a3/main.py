from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sympy.ntheory.modular import crt
from gmpy2 import iroot

def main() -> None:
    keys = [None] * 3
    messages = [None] * 3

    # read all public keys and encrypted messages and store them in two separate lists
    for i in range(3):
        with open(f'pk{i + 1}.pem', 'r') as fin:
            keys[i] = RSA.importKey(fin.read())

        with open(f'msg{i + 1}.bin', 'rb') as fin:
            messages[i] = bytes_to_long(fin.read())

    # use the chinese remainder theorem and calculate x = m^3
    x = crt([key.n for key in keys], messages)[0]
    # find m by calculating the cube root of x
    cbrt_x, exact = iroot(x, 3)

    # if the cube root of x is exact, print the decrypted message
    if exact:
        print(long_to_bytes(cbrt_x).decode())

if __name__ == '__main__':
    main()
