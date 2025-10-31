import re
from pathlib import Path

import nh3
from bs4 import BeautifulSoup
from rich import print

from stalkers_cli.utils import ALLOWED_TAGS, OUTPUT_FOLDER_NAME, dump_json


def parse_html(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()


def sanitize(html: str):
    clean_html = nh3.clean(html, tags=ALLOWED_TAGS)
    soup = BeautifulSoup(clean_html, "html.parser")

    for tag in soup.find_all():
        if tag.name == "h1":
            tag.decompose()

    final_html = str(soup)
    final_html = (
        final_html
        .replace('"', "&quot;")
        .replace("'", "&#39;")
        .replace("\n", " ")
    )
    final_html = re.sub(r'\s+', ' ', final_html).strip()
    return final_html


def get_chapters(html: str, chapter_container_className: str):
    sanitized_chapters = []
    soup = BeautifulSoup(html, "html.parser")
    chapters = soup.find_all("div", class_=[chapter_container_className])
    for index, chapter in enumerate(chapters):
        sanitized_chapters.append(sanitize(str(chapter)))

    return sanitized_chapters


def dump_chapters_json(output_folder: Path, chapters: list[str]):
    output_file = output_folder / "chapters.json"
    chapters_dict = []

    for index, chapter in enumerate(chapters):
        chapter_number = index + 1
        chapter_dict = {
            "number": chapter_number,
            "title": f"Chapter {chapter_number}",
            "body": chapter,
        }
        chapters_dict.append(chapter_dict)
    
    dump_json(output_path=output_file, data=chapters_dict)


def merge_books(root_path: Path):
    full_book = ""
    for book in root_path.glob("book*.html"):
        full_book += f"\n{parse_html(book)}"
    
    with open(root_path/"full.html", "w", encoding="utf-8") as html_file:
        html_file.write(full_book)


if __name__ == "__main__":
    root_path = Path(r'C:\Users\bob\Downloads\furia-vermelha')
    output_folder = Path(f"{root_path}/{OUTPUT_FOLDER_NAME}")
    output_folder.mkdir(parents=True, exist_ok=True)

    merge_books(root_path)
    html_path = root_path / "full.html"

    html_str = parse_html(html_path)
    chapters = get_chapters(html_str, chapter_container_className="chapter-element")

    dump_chapters_json(output_folder=output_folder, chapters=chapters)
