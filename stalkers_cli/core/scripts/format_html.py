import os
from pathlib import Path

from bs4 import BeautifulSoup
from rich import print
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn)

progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)


def parse_html(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()


def do(soup: BeautifulSoup, stop: dict[str, str]):
    stops = soup.find_all(stop["tag"], class_=[stop["className"]])

    with progress_bar as p:
        for value in p.track(range(len(stops)), description="Formating book HTML"):    
            if stops[value].find_parent("article", class_="block"):
                continue

            wrapper = soup.new_tag("article", attrs={
                "class": "block",
                "id": f"chapter-{value+1}"
            })

            stops[value].insert_before(wrapper)

            wrapper.append(stops[value].extract())

            current = wrapper
            next_tag = current.find_next_sibling()

            while next_tag and next_tag not in stops:
                to_move = next_tag
                next_tag = to_move.find_next_sibling()
                wrapper.append(to_move.extract())
        

def write(soup: BeautifulSoup, root: Path):
    output = root / "formatted.html"
    with open(output, "w", encoding="utf-8") as html_file:
        html_file.write(str(soup))


def format_book(root: Path, stop: dict[str,str]):
    book = root / "book.html"
    soup = BeautifulSoup(parse_html(book), "html.parser")
    
    do(soup, stop)
    write(soup, root)


if __name__ == "__main__":
    stop = {"tag": "div", "className": "chapter"}
    root = Path(r"C:\Users\bob\Desktop\blackflame")

    format_book(root, stop)