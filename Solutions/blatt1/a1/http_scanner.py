from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from re import search

def main() -> None:
    args = parse_arguments()

    print('[*] Checking for open ports and identifying HTTP services...')

    # spawn and start a new thread for each port from 1 to 65535
    for port in range(1, 65536):
        thread = Thread(target=check_port, args=(args.ip, port))

        thread.start()

def check_port(ip: str, port: int) -> None:
    # create a TCP socket with IPv4 address family
    connection = socket(AF_INET, SOCK_STREAM)
    # connect to the server on a specific port
    status = connection.connect_ex((ip, port))

    # if the connection is successful
    if status == 0:
        # send an HTTP GET request
        connection.send(b'GET / HTTP/1.1\r\nHost: test\r\n\r\n')

        try:
            # save the response into a variable and decode it
            response = connection.recv(4096).decode(errors='ignore').strip()
            # try to identify the HTTP service
            service = identify_httpd(response)
        except Exception:
            service = None

        if service:
            print(f'[+] {ip}:{port} ({service})')

    connection.close()

def identify_httpd(response: str) -> str:
    # search for the string 'Server:' and map everything until the end of the line (.*)
    server = search(r'Server:.*', response)

    # if a match is found, remove the string 'Server:' and spaces on both sides and return it
    if server:
        return server.group(0).replace('Server:', '').strip()

    return None

def parse_arguments() -> object:
    parser = ArgumentParser(description='HTTP Port Scanner')

    parser.add_argument('-i', '--ip', dest='ip', type=str, required=True, help='The IP address of the target')

    return parser.parse_args()

if __name__ == '__main__':
    main()
