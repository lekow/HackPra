from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from socket import socket, AF_INET, SOCK_STREAM


# TRANSFER AMOUNT $1000000 REASON Salary Jan. 2016 DEST #78384 END
MESSAGE = 'wUHhFdm5le/fLoF/G4U0u6FGSNVtkxFA3ZIEwYombzhGF2eYUCOutHTg0h16BtYlBd5FO/XlJkQ058Ev+8hTIA=='
IP, PORT = '10.0.23.61', 1337

def main() -> None:
    # base64 decode the message first
    message = b64decode(MESSAGE)
    # change the destination part of the message to #31337
    message = change_destination(message, len(message))

    # do the transfer and send $1,000,000 to #31337
    do_transfer(message)

def change_destination(message: bytes, length: int) -> str:
    result = []
    # one plaintext block of the encrypted message
    message_end_real = b' DEST #78384 END'
    # the message that we want to replace the block to
    message_end_replace = b' DEST #31337 END'

    # replace all bytes starting at position 32 and ending at 48 by calculating _C[i - 1] = C[i - 1] xor P[i] xor M[i]
    for i in range(15, -1, -1):
        result.append(message[length - i - 17] ^ message_end_real[15 - i] ^ message_end_replace[15 - i])

    # create a new payload by replacing all bytes starting a position 32 and ending at 48 by the bytes we just calculated
    payload = b''.join([message[:32], bytes(result), message[48:]])

    # return the payload as base64 encoded string
    return b64encode(payload).decode()

def do_transfer(message: str) -> None:
    # create a TCP socket with IPv4 address family
    connection = socket(AF_INET, SOCK_STREAM)
    # connect to the server on a specific port
    status = connection.connect_ex((IP, PORT))

    # if the connection is successful, send the transaction and print the response
    if status == 0:
        connection.send(f'{message}\n'.encode())
        response = connection.recv(4096)

        print(response.decode(errors='ignore').strip())

    connection.close()

if __name__ == '__main__':
    main()
