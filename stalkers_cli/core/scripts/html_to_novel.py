import re
from pathlib import Path

import nh3
from bs4 import BeautifulSoup
from rich import print

from stalkers_cli.utils import ALLOWED_TAGS, OUTPUT_FOLDER_NAME, dump_json, load_json


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


def dump_novel_json(output_folder: Path, title: str, author: str):
    novel_file = output_folder / "novel.json"
    chapters_file = output_folder / "chapters.json"

    chapters = load_json(chapters_file)
    novel_dict = {
        "title": title,
        "author": author,
        "status": "COMPLETED",
        "description": "",
        "genres": [], 
        "tags": [],
        "chapters": chapters
    }

    dump_json(output_path=novel_file, data=novel_dict)

def merge_books(root_path: Path):
    full_book = ""
    for book in root_path.glob("book*.html"):
        full_book += f"\n{parse_html(book)}"
    
    with open(root_path/"full.html", "w", encoding="utf-8") as html_file:
        html_file.write(full_book)


if __name__ == "__main__":
    root_path = Path(r'C:\Users\bob\Desktop\super-powereds-year-1')
    output_folder = Path(f"{root_path}/{OUTPUT_FOLDER_NAME}")
    output_folder.mkdir(parents=True, exist_ok=True)

    merge_books(root_path)
    html_path = root_path / "full.html"

    html_str = parse_html(html_path)
    chapters = get_chapters(html_str, chapter_container_className="mbppagebreak")

    dump_chapters_json(output_folder=output_folder, chapters=chapters)
    # dump_novel_json(output_folder=output_folder, title="Super Powereds: Year 1", author="Drew Hayes")
