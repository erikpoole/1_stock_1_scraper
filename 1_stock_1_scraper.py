from bs4 import BeautifulSoup
import os
import requests
import re
import sys

BASE_URL = "http://www.1stock1.com"
OUTPUT_FOLDER = "output"

CONSECTUTIVE_FAILURE_LIMIT = 200

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    count = 1
    consecutive_failures = 0
    while consecutive_failures < CONSECTUTIVE_FAILURE_LIMIT:
        targetted_url = f"{BASE_URL}/1stock1_2582.htm"
        count += 1
        try:
            raw_page = requests.get(targetted_url)
            soup = BeautifulSoup(raw_page.content, "html.parser")

            stock_name = get_stock_name(soup)
            file_name = create_file_name(stock_name)

            returns_table = get_returns_table(soup)
            returns = get_returns(returns_table)
            output_text = parse_returns(returns)

            create_file(file_name, output_text)
            consecutive_failures = 0

        except Exception as error:
            print(f"{targetted_url} failed; {error}")
            consecutive_failures += 1

        break

def get_stock_name(soup):
    title_indicator = " Yearly Returns"
    raw_title = soup.find(text=re.compile(title_indicator))
    if raw_title == None:
        raise Exception("page does not match stock history format")

    raw_stock_name = raw_title[:raw_title.find(title_indicator)]
    return raw_stock_name.strip()

def get_returns_table(soup):
    for table_element in soup.find_all("table"):
        if table_element.parent.name == "div":
            return table_element

def get_returns(table):
    returns = []
    for count, table_row in enumerate(table.find_all("tr")):
        # skip table header
        if count == 0:
            continue
        # additional error checking needed
        row_spans = table_row.find_all("span")
        returns.append([row_spans[0].text, row_spans[4].text])
    
    return returns

def parse_returns(returns):
    parsed = ""
    for value in returns:
        parsed += f"{value[0]} {value[1]}\n"
    
    return parsed

def create_file_name(text):
    invalid_chars = ["\\", "/", ":", "*", "?", "/", "<", ">", "|"]

    cleaned_text = text
    for invalid_char in invalid_chars:
        cleaned_text = cleaned_text.replace(invalid_char, " ")
    return f"{cleaned_text}.txt"

def create_file(file_name, text):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(working_dir, OUTPUT_FOLDER, file_name)
    with open(output_path, "w") as file:
        file.write(text)


if __name__ == "__main__":
    main()
