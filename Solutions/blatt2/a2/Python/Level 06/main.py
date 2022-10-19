from requests import Session
from re import findall, search
from hashlib import md5

URL = 'http://10.0.23.24:8080/python/level06/index.php'
HEADERS = {'Authorization': 'Basic d29ya3Nob3A6d29ya3Nob3A='}

def main() -> None:
    # create a new session and set headers
    session = Session()
    session.headers = HEADERS

    # extract the MD5 hash values of the first request
    response = session.get(URL)
    list1 = extract_all_md5(response.text)

    # extract the MD5 hash values of the second request
    response = session.get(URL)
    list2 = extract_all_md5(response.text)

    # find the one element that exists in the second list, but not the first one and submit it via a POST request to get the flag
    for item in list2:
        if item not in list1:
            response = session.post(URL, data={'new_value': item})
            break

    # extract the keyword, calculate the MD5 hash value of it and print it as the flag
    print_flag(response.text)

# extract all MD5 hash values from the webpage by using regular expressions and return them
def extract_all_md5(content: str) -> list:
    md5s = findall(r'[0-9a-fA-F]{32}', content)

    if md5s:
        return md5s

    return []

# calculate the MD5 hash value of the extracted flag keyword and print it
def print_flag(content: str) -> None:
    keyword = extract_flag_keyword(content)

    if keyword:
        print(f'fau-ctf-{md5(keyword.encode()).hexdigest()}')

# extract the keyword of the flag in order to be able to calculate the MD5 hash value of it
def extract_flag_keyword(content: str) -> str:
    keyword = search(r'fau-ctf-md5sum\(.*\)', content)

    if keyword:
        return keyword.group(0).replace('fau-ctf-md5sum(', '').strip()[:-1]

    return None

if __name__ == '__main__':
    main()
