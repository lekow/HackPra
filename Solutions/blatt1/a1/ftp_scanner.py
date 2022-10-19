from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM

PORTS = [210, 2100, 2121, 21000]
FTP_FINGEPRINTS = {
    '331 Password required for anonymous': 'pro-ftpd',
    '331 User anonymous OK. Password required': 'pure-ftpd',
    '331 Give me password': 'py-ftpd',
    '331 Please specify the password.': 'vs-ftpd'
}

def main() -> None:
    args = parse_arguments()

    print('[*] Checking for open ports and identifying FTP services...')

    for port in PORTS:
        check_port(args.ip, port)

def check_port(ip: str, port: int) -> None:
    # create a TCP socket with IPv4 address family
    connection = socket(AF_INET, SOCK_STREAM)
    # connect to the server on a specific port
    status = connection.connect_ex((ip, port))

    # if the connection is successul
    if status == 0:
        # send the command 'USER anonymous' and ignore the response
        connection.send(b'USER anonymous\r\n')
        connection.recv(4096)
        # send the command 'USER anonymous' once more
        connection.send(b'USER anonymous\r\n')

        try:
            # save the response into a variable and decode it
            response = connection.recv(4096).decode(errors='ignore').strip()
            # try to identify the FTP service
            service = identify_ftpd(response)
        except Exception:
            service = None

        if service:
            print(f'[+] {ip}:{port} ({service})')

    connection.close()

def identify_ftpd(response: object) -> str:
    # map the response to the pre-defined responses in FTP_FINGEPRINTS
    return FTP_FINGEPRINTS.get(response, None)

def parse_arguments() -> object:
    parser = ArgumentParser(description='FTP Port Scanner')

    parser.add_argument('-i', '--ip', dest='ip', type=str, required=True, help='The IP address of the target')

    return parser.parse_args()

if __name__ == '__main__':
    main()
