from ecdsa import VerifyingKey, SigningKey
from ecdsa.ecdsa import Signature
from ecdsa.der import remove_sequence, remove_integer
from ecdsa.util import sigdecode_der, sigencode_der
from Crypto.Util.number import bytes_to_long, inverse
from hashlib import sha256


class Message():
    def __init__(self: object, message: bytes, signature: bytes, hash: str) -> None:
        self.message = message
        self.r, self.s = get_rs(signature)
        self.h = int(hash, 16)
        self.signature = signature


def main() -> None:
    # load the verifying key
    with open('vk.pem', 'r') as fin:
        vkey = VerifyingKey.from_pem(fin.read())

    # load both messages and their corresponding signature, and also calculate the hash of each message
    messages = load_messages(vkey)

    # extract the modulus from the verifying key
    n = vkey.pubkey.order

    # get the r value (same for both signatures)
    r = messages[0].r
    # get both hash values
    h1, h2 = messages[0].h, messages[1].h
    # get both s values
    s1, s2 = messages[0].s, messages[1].s

    # calculate the ephemeral key
    k = (inverse(s1 - s2, n) * (h1 - h2)) % n
    # calculate the private key
    d = (inverse(r, n) * (k * s1 - h1)) % n

    print(f'[*] Ephemeral key: {k}')
    print(f'[*] Private key: {d}')

    # use the private key and the verifying key to create a new signing key
    skey = SigningKey.from_secret_exponent(d, curve=vkey.curve, hashfunc=vkey.default_hashfunc)

    # check if the public key of the verifying key and the newly created signing key match
    if vkey.pubkey == skey.get_verifying_key().pubkey:
        print('[+] Both public keys match! Saving new signature and signing key...')

        # read our message that needs to be signed
        with open('msg3.txt', 'rb') as fin:
            message = fin.read()

        # create a new signature for that message
        signature = skey.sign(message, sigencode=sigencode_der)

        # save the newly created signature
        with open('msg3.sig', 'wb') as fout:
            fout.write(signature)

        # save the signing key in PEM format
        with open('sk.pem', 'w') as fout:
            fout.write(skey.to_pem().decode())
    else:
        print('[-] Both public keys do not match, exiting...')
        exit(1)

# load both messages and their corresponding signature, and also calculate the hash of each message
def load_messages(vkey: VerifyingKey) -> list:
    messages = [None] * 2

    for i in range(2):
        # load message
        with open(f'msg{i + 1}.txt', 'rb') as fin:
            message = fin.read()

        # load signature
        with open(f'msg{i + 1}.sig', 'rb') as fin:
            signature = fin.read()

        # calculate the hash of the message
        hash = vkey.default_hashfunc(message).hexdigest()
        # save data as an instance of the Message class
        messages[i] = Message(message, signature, hash)

    return messages

# extract the (r, s) values for a signature
def get_rs(signature: bytes) -> tuple:
    rs, _ = remove_sequence(signature)
    r, s = remove_integer(rs)
    s, _ = remove_integer(s)

    return r, s

if __name__ == '__main__':
    main()
