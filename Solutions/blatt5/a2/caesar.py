
def rot(s: str, n: int) -> str:
    # used for saving the results
    r = []

    # iterate over each char in the string
    for c in s:
        # get the integer value of the character
        m = ord(c)

        # if the character is lower-/uppercase, add n to it
        if c.islower() or c.isupper():
            m += n

            # evaluate lowercase chars only into the char-space a..z and
            # uppercase chars only into the char-space A..Z
            if c.islower() and m > ord('z'):
                m = ord('a') + m % ord('z') - 1
            elif c.isupper() and m > ord('Z'):
                m = ord('A') + m % ord('Z') - 1

        # append the character to the result
        r.append(chr(m))

    # join all characters and return them
    return ''.join(r)

# utilizes rot with a rotation of 13
def caesar(s: str) -> str:
    return rot(s, 13)

def main() -> None:
    print(caesar('erqcryvpnaoyhrgvtre'))

if __name__ == '__main__':
    main()
