from ast import List
from pathlib import Path
from typing import ClassVar, Tuple

import nh3
from bs4 import BeautifulSoup
from rich import print
from utils import ALLOWED_TAGS, BLACKLIST_SET, dump_json, load_json


class Format:
    downloaded_chapters_folder: ClassVar[Path]
    output_folder: ClassVar[Path]
    chapters_data: ClassVar[List]

    def __init__(self, root_path: Path, output_folder=Path):
        self.downloaded_chapters_folder = Path(f"{root_path}/json")
        self.output_folder = output_folder
        self.chapters_data = []


    def __dump_chapters_array(self):
        """
        dumps the formatted chapters into the output folder.
        Should be called after the extraction only.
        """
        first_chapter = self.chapters_data[0].get("number")
        last_chapter = self.chapters_data[-1].get("number")
        self.output_file = Path(f"{self.output_folder}/chapters_{first_chapter}-{last_chapter}.json")
        dump_json(self.output_file, self.chapters_data)



    def __extract_chapters(self):
        """
        Load all chapters, sanitize them up, validate them and put them in an array.
        """
        for chapter_file in self.downloaded_chapters_folder.glob("*.json"):
            chapter_data = load_json(chapter_file)

            chapter_title = chapter_data.get("title")
            chapter_body = self.__sanitize_body(html=chapter_data.get("body"), chapter_title=chapter_title)
            chapter_id = chapter_data.get("id")
            chapter_number = chapter_id

            self.__body_validation(chapter_body, chapter_id)


            self.chapters_data.append(
                {
                    "id": chapter_id,
                    "number": chapter_number,
                    "title": chapter_title,
                    "body": chapter_body,
                }
            )


    def __extract_range_chapters(self, range: Tuple[int, int]):
        """
        Load the requested range of chapters, sanitize them up, validate them and put them in an array.
        """
        initial_range, final_Range = range
        for chapter_file in self.downloaded_chapters_folder.glob("*.json"):
            chapter_data = load_json(chapter_file)
            chapter_id = chapter_data.get("id")

            if (chapter_id >= initial_range and chapter_id <= final_Range):
                chapter_title = chapter_data.get("title")
                chapter_body = self.__sanitize_body(html=chapter_data.get("body"), chapter_title=chapter_title)

                self.__body_validation(chapter_body, chapter_id)

                self.chapters_data.append(
                {
                    "id": chapter_id,
                    "number": chapter_id,
                    "title": chapter_title,
                    "body": chapter_body,
                }
            )


    def __body_validation(self, body: str, chapter_id: int):
        """
        Sometimes, the chapter is null or has less text than it should. 
        If so, a warning print will be executed
        """
        if body is None or len(body) < 50:
            print(f"[bold red]Chapter of id {chapter_id} is suspicious[/bold red]")



    def __sanitize_body(self, html: str, chapter_title: str):
        """"
        Removes unwanted tags, text and data from the body html.
        """
        clean_html = nh3.clean(html, tags=ALLOWED_TAGS)
        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup.find_all():
            text = tag.get_text(strip=True).lower()
            if any(bad_text in text for bad_text in BLACKLIST_SET):
                tag.decompose()

            if tag.name == "p":
                p_text = tag.get_text(strip=True).lower()

                # Some novels have the chapter title in a <p> tag. If so, then remove it.
                if p_text == chapter_title.lower().strip():
                    tag.decompose()

            if tag.name == "h1":
                tag.decompose()

        # Sometimes, the chapter title is written as pure text (not inside an html tag)
        # This is to delete them
        for element in soup.find_all(string=True):
            if (
                element.strip().lower() == chapter_title.strip().lower()
                and element.parent.name not in {"h1", "h2", "h3", "p"}
            ):
                element.extract()

        final_html = str(soup)

        final_html = final_html.replace('"', "&quot;").replace("'", "&#39;")

        return final_html
    

    def execute_range(self, range: Tuple[int, int]):
        self.__extract_range_chapters(range)
        self.__dump_chapters_array()


    def execute(self):
        self.__extract_chapters()
        self.__dump_chapters_array()
