from hashlib import md5

def main() -> None:
    # read all lines from sort_this_too.txt, strip them and store them
    with open('sort_this_too.txt', 'r') as fin:
        lines = [line.strip() for line in fin.readlines()]

    # filter all lines that do not start with 'aa' or end with 'ee'
    lines = list(filter(startswith, lines))
    # join all remaining strings in the list and calculate their MD5 hash value
    print(md5(''.join(lines).encode()).hexdigest())

# returns true if line starts with 'aa' or ends with 'ee'; else, returns false
def startswith(line: str) -> bool:
    return line.startswith('aa') or line.endswith('ee')

if __name__ == '__main__':
    main()
