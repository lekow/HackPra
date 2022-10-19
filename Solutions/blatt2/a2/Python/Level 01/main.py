from hashlib import md5

def main() -> None:
    # read all lines from sort_this.txt, strip them and store them
    with open('sort_this.txt', 'r') as fin:
        lines = [line.strip() for line in fin.readlines()]

    # sort all lines
    lines = sorted(lines)
    # join all strings in the list and calculate their MD5 hash value
    print(md5(''.join(lines).encode()).hexdigest())

if __name__ == '__main__':
    main()
