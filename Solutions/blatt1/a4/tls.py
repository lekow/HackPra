from OpenSSL import SSL
from socket import socket, AF_INET, SOCK_STREAM


class TLSConnection():
    # constructor
    def __init__(self: object, host: str, port: int) -> None:
        # create a HTTPS connection by using the TLSv1.2 protocol
        self.__connection = SSL.Connection(SSL.Context(SSL.TLSv1_2_METHOD), socket(AF_INET, SOCK_STREAM))
        # connect to the server on a specific port
        self.__connection.connect((host, port))

    # destructor
    def __del__(self: object) -> None:
        self.__connection.close()

    def do_handshake(self: object, barrier: object, counter: object) -> None:
        # wait until all threads have connected to the target
        barrier.wait()

        try:
            # launch handshake
            self.__connection.send(b'test')
        except Exception:
            # increment the failed counter
            counter.failed()
            return

        # increment the success counter
        counter.success()
