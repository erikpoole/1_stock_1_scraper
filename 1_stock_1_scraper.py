from bs4 import BeautifulSoup
import os
import requests
import re
import sys

BASE_URL = "http://www.1stock1.com"
OUTPUT_FOLDER = "output"

def main():
    # probably don't fail for everything...
    # store invalid request pages in log file
    for value in range(1):
        targetted_url = f"{BASE_URL}/1stock1_148.htm"
        try:
            raw_page = requests.get(targetted_url)
            soup = BeautifulSoup(raw_page.content, "html.parser")

            title = get_title(soup)
            if title == "":
                print("WARNING: file without title")

            returns_table = get_returns_table(soup)
            returns = get_returns(returns_table)
            output_text = parse_returns(returns)

            os.makedirs(OUTPUT_FOLDER, exist_ok=True)
            create_file(f"{title}.txt", output_text)

        except Exception as error:
            print(f"{targetted_url} failed; {error}")



def get_title(soup):
    title_indicator = " Yearly Returns"
    raw_title = soup.find(text=re.compile(title_indicator))
    return raw_title[:raw_title.find(title_indicator)]

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

def create_file(file_name, text):
    working_dir = os.path.dirname(os.path.realpath(__file__))
    output_path = os.path.join(working_dir, OUTPUT_FOLDER, file_name)
    with open(f"output/{file_name}", "w") as file:
        file.write(text)


if __name__ == "__main__":
    main()
