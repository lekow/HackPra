from requests import Session
from re import search

URL = 'http://10.0.23.24:8080/python/level05/index.php'
HEADERS = {'Authorization': 'Basic d29ya3Nob3A6d29ya3Nob3A='}

def main() -> None:
    # create a new session and set headers
    session = Session()
    session.headers = HEADERS
    # send a GET request to get the contents
    response = session.get(URL)

    # extract the secret, as well as the equation and solve it
    secret = extract_secret(response.text)
    equation = extract_equation(response.text)
    result = solve_equation(equation)

    # if either the secret or the result we're not extracted, exit
    if not secret or not result:
        exit()

    # if both the secret and result are successfully extracted, submit them via a POST request
    data = {'secret': secret, 'result': result}
    response = session.post(URL, data=data)

    # extract the flag by using a regular expression and print it
    print_flag(response.text)

def extract_secret(content: str) -> str:
    # extract the secret by using a regular expression
    secret = search(r'Your secret is:.*', content)

    # if the secret is successfully extracted, remove the string 'Your secret is:' from it, strip it and return it
    if secret:
        return secret.group(0).replace('Your secret is:', '').strip()

    return None

def extract_equation(content: str) -> str:
    # extract the equation by using a regular expression
    equation = search(r'Please solve for us:.*', content)

    # if the equation is successfully extracted, remove the string 'Please solve for us:' from it, strip it and return it
    if equation:
        return equation.group(0).replace('Please solve for us:', '').strip()

    return None


# identify the operation in the equation and return the result of it
def solve_equation(equation: str) -> int:
    for operation in {'+', '-', '*', '/'}:
        if operation in equation:
            num1, num2 = equation.split(f' {operation} ')

            if operation == '+':
                return int(num1) + int(num2)
            elif operation == '-':
                return int(num1) - int(num2)
            elif operation == '*':
                return int(num1) * int(num2)
            else:
                return int(num1) / int(num2)

    return None

def print_flag(content: str) -> None:
    # extract the flag by using a regular expression
    flag = search(r'fau-ctf-\w{25}', content)

    # if the flag is found, print it
    if flag:
        print(flag.group(0))

if __name__ == '__main__':
    main()
