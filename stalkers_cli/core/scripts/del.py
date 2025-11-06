from pathlib import Path
from bs4 import BeautifulSoup

def parse_html(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()

input = Path(r"C:\Users\bob\Desktop\super-powereds-year-1\book.html")
output = Path(r"C:\Users\bob\Desktop\super-powereds-year-1\book-f.html")

soup = BeautifulSoup(parse_html(input), "html.parser")

chapters = soup.find_all("div", class_="mbppagebreak")

for chapter in chapters:
    paragraph = chapter.find_next_sibling()

    while paragraph and paragraph.name == "p":
        next = paragraph
        paragraph = next.find_next_sibling()
        chapter.append(next.extract())

with open(output, "w", encoding="utf-8") as html_file:
    html_file.write(str(soup))