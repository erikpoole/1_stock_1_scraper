from bs4 import BeautifulSoup
import os
import requests
import re
import sys

BASE_URL = "http://www.1stock1.com"
OUTPUT_FOLDER = "output"
ERR_LOG_FILE_NAME = "errors.txt"

DEFAULT_ERR_TEXT = "page does not match stock history format"

CONSECTUTIVE_FAILURE_LIMIT = 200


def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    error_log = create_error_log()

    request_count = 1
    errString = ""
    consecutive_failures = 0
    while consecutive_failures < CONSECTUTIVE_FAILURE_LIMIT:
        targetted_url = f"{BASE_URL}/1stock1_{request_count}.htm"

        if request_count % 100 == 1:
            print(f"requesting and parsing {targetted_url}")

        request_count += 1

        try:
            raw_page = requests.get(targetted_url)
            soup = BeautifulSoup(raw_page.content, "html.parser")

            stock_name = get_stock_name(soup)
            file_name = create_file_name(stock_name)

            returns_table = get_returns_table(soup)
            returns = get_returns(returns_table)
            output_text = parse_returns(returns)

            write_file(file_name, output_text)
            consecutive_failures = 0

        except Exception as error:
            error_log.write(f"{targetted_url} failed; {error}\n")
            consecutive_failures += 1

    error_log.close()


def get_stock_name(soup):
    title_indicator = " Yearly Returns"
    raw_title = soup.find(text=re.compile(title_indicator))
    if raw_title is None:
        raise Exception(f"{DEFAULT_ERR_TEXT}; `Yearly Returns` not found")

    raw_stock_name = raw_title[:raw_title.find(title_indicator)]
    return raw_stock_name.strip()


def get_returns_table(soup):
    for table_element in soup.find_all("table"):
        if table_element.parent.name == "div":
            return table_element

    raise Exception(f"{DEFAULT_ERR_TEXT}; returns table not found")


def get_returns(table):
    returns = []
    for row_number, table_row in enumerate(table.find_all("tr")):
        table_cells = table_row.find_all("td")

        if len(table_cells) != 5:
            if row_number == 0:
                raise Exception(f"{DEFAULT_ERR_TEXT}; unexpected number of columns found in returns table row")

            continue

        if row_number == 0:
            if not "Year" in table_cells[0].text:
                raise Exception(f"{DEFAULT_ERR_TEXT}; table does not include `Year` column")

            if not "Percent Gain or Loss" in table_cells[4].text:
                raise Exception(f"{DEFAULT_ERR_TEXT}; table does not include `Percent Gain or Loss` column")

            continue

        returns.append([table_cells[0].text, table_cells[4].text])

    if returns == []:
        raise Exception(f"{DEFAULT_ERR_TEXT}; no rows found in returns table")

    return returns


def parse_returns(returns):
    parsed = ""
    for value in returns:
        parsed += f"{value[0].strip()} {value[1].strip()}\n"

    return parsed


def create_file_name(text):
    invalid_chars = ["\\", "/", ":", "*", "?", "/", "<", ">", "|"]

    cleaned_text = text
    for invalid_char in invalid_chars:
        cleaned_text = cleaned_text.replace(invalid_char, " ")
    return f"{cleaned_text}.txt"


def write_file(file_name, text):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(working_dir, OUTPUT_FOLDER, file_name)
    with open(output_path, "w") as file:
        file.write(text)


def create_error_log():
    working_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(working_dir, ERR_LOG_FILE_NAME)
    return open(output_path, "w")


if __name__ == "__main__":
    main()
