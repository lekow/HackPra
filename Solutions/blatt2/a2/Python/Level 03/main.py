from hashlib import sha1, md5

SHA1_HASH = 'fd8b6b5944fcede476bd62989044bd0fa36400e8'
DIGITS_START = '36979765629224074726367327745686243'

def main() -> None:
    i = 0

    while True:
        # create a five digit number of type string
        digits = str(i).zfill(5)

        # check if the five random digits are the correct digits
        if not sha1hash(digits):
            i += 1
            continue

        # calculate the MD5 hash value of the found whole 40 digits number
        print(md5((DIGITS_START + digits).encode()).hexdigest())
        break

# returns true if the correct five digits have been found; else, returns false
def sha1hash(digits: str) -> bool:
    # calculate the SHA1 hash value of the partial hash concatenated with five random digits
    hash = sha1((DIGITS_START + digits).encode()).hexdigest()

    # return true if the calculated hash matches the pre-defined hash; else, return false
    if hash == SHA1_HASH:
        return True

    return False

if __name__ == '__main__':
    main()
