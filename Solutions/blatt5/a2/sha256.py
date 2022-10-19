from hashlib import sha256
from multiprocessing import Pool, Event


SPECIAL_CHARS = ['!', '?', '.', ',']
HASH = 'a0a585828a2644361236d2ca69345d3bc15eb940a401d6e50f59f7ce3080c06f'

# init function for the Pool
def init(e):
    global event
    event = e

def check_password(password: str) -> None:
    # if event is set, i.e. password is found, return
    if event.is_set():
        return

    # create a SHA256 hash of the password
    hash = sha256(password.encode()).hexdigest()

    # if the new hash matches the given hash, print it and
    # set the event so that no more passwords are tried
    if hash == HASH:
        print(password)
        event.set()

def main() -> None:
    # load words from file
    with open('words.lst', 'r') as fin:
        words = [word.strip() for word in fin.readlines()]

    # create an empty list and an event
    passwords, e = [], Event()

    # create new passwords by appending the special characters
    for word in words:
        for special_char in SPECIAL_CHARS:
            passwords.append(word + special_char)

    # create a pool and pass the event to it
    with Pool(initializer=init, initargs=(e,)) as pool:
        pool.map(check_password, passwords)

if __name__ == '__main__':
    main()
