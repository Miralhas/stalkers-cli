import logging
import re
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, List, Literal

import nh3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scripts.metadata.funcs import dump_json, load_json

AVAILIABLE_SOURCES = ["webnoveldotcom", "novelupdates"]

class AvailableSources(str, Enum):
    webnoveldotcom = "webnoveldotcom"
    novelupdates = "novelupdates"

# Categoris Array - (Genres) - https://www.novelupdates.com/genre-explanation/
CATEGORIES = [
    "action",
    "adult",
    "adventure",
    "comedy",
    "drama",
    "ecchi",
    "fantasy",
    "gender bender",
    "harem",
    "historical",
    "horror",
    "josei",
    "martial arts",
    "mature",
    "mecha",
    "mystery",
    "psychological",
    "romance",
    "school life",
    "sci-fi",
    "seinen",
    "shoujo",
    "shoujo ai",
    "shounen",
    "shounen ai",
    "slice of life",
    "smut",
    "sports",
    "supernatural",
    "tragedy",
    "wuxia",
    "xianxia",
    "xuanhuan",
    "yaoi",
    "yuri",
]

class MetadataSource(ABC):
    def __init__(self, root_path: Path, novel_name: str):
        self.output_path = Path("./current_metadata.json")
        self.root_path = root_path
        self.novel_name = novel_name

    @property
    @abstractmethod
    def base_url(self):
        pass

    @property
    def url(self):
        return self.base_url + self.novel_name

    @abstractmethod
    def get_metadata(self):
        pass

    def format_metadata(self, metadata_dict: Dict) -> None:
        pass

    def clean_html(self, html: str) -> str:
        """format and clean given html

        Args:
            html (str): html to be cleaned / formatted

        Returns:
            str: formatted html
        """
        nh3_tags = nh3.ALLOWED_TAGS - {'div', 'br', 'strong'}
        html = nh3.clean(html, tags=nh3_tags)

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all():
            if "class" in tag.attrs:
                del tag["class"]

        final_html = (
            str(html).replace('"', "&quot;").replace("'", "&#39;").replace("\n", "")
        )

        return final_html

    def merge_current_metadata_to_novel_metadata(self):
        json_to_merge_path = Path(f"{self.root_path}/meta.json")
        try:
            chapters = load_json(json_to_merge_path).get("novel").get("chapters")
            current_metadata_dict = load_json(self.output_path)

            current_metadata_dict["chapters"] = chapters

            new_dict = {"novel": current_metadata_dict}

            dump_json(Path(json_to_merge_path), new_dict)

            logging.info(f"{json_to_merge_path} got successfully merged!")
        except Exception as e:
            logging.error(f"Failed to merge {json_to_merge_path}: {e}")

    def execute(self):
        self.get_metadata()
        self.merge_current_metadata_to_novel_metadata()

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class WebnovelDotComSource(MetadataSource):
    def __init__(self, root_path: Path, novel_name: str):
        super().__init__(root_path, novel_name)
        self.tags_map = {
            "weaktostrong": "weak to strong",
            "sliceoflife": "slice of life",
            "kingdombuilding": "kingdom building",
            "no-harem": "no harem",
            "nonhuman": "non-human",
            "sweetlove": "sweet love",
            "levelup": "level up",
            "sweetlove": "sweet love",
            "thestrongactingweak": "the strong acting weak",
            "bloodpumping": "blood pumping"
        }
        self.required_metadata_properties = ["og:title", "og:author", "og:tag"]

    @property
    def base_url(self) -> Literal['https://www.webnovel.com/book/']:
        return "https://www.webnovel.com/book/"

    def format_metadata(self, metadata_dict):
        """formats given dict to stalkers-api standards

        Args:
            metadata_dict (Dict): dict containing metadata retrieved through selenium
        """
        tags: List[str] = metadata_dict.get("tag").split(", ")
        tags = [tag.lower().strip() for tag in tags]

        # some tags on Webnovel.com don't have spacing between words. This is a mapping to those tags. "WEAKTOSTRONG" -> "Weak to Strong"
        tags = [
            self.tags_map[tag] if tag in self.tags_map.keys() else tag for tag in tags
        ]

        metadata_dict["genres"] = [
            genre for genre in CATEGORIES if genre.lower().strip() in tags
        ]

        metadata_dict["tags"] = tags
        del metadata_dict["tag"]

        metadata_dict["title"] = metadata_dict["title"].lower()

    def get_metadata(self):
        driver = webdriver.Firefox()
        meta_data = {}
        try:
            driver.get(self.url)

            wait = WebDriverWait(driver, 10)
            # ultima meta tag
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "html/head/meta[@property='og:site_name']")
                )
            )

            meta_tags = driver.find_elements(By.XPATH, "html/head/meta")

            for meta in meta_tags:
                meta_property = meta.get_attribute("property")

                if (meta_property is not None and meta_property in self.required_metadata_properties):
                    meta_name = meta_property.replace("og:", "")
                    meta_content = meta.get_attribute("content")
                    meta_data.update({meta_name: meta_content})

            novel_description_html = driver.find_element(By.CSS_SELECTOR, ".g_wrap .j_synopsis p").get_attribute("outerHTML")
            novel_description_html = self.clean_html(novel_description_html)

            try:
                novel_status = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div[2]/div[1]/strong[1]/span")
                novel_status = "COMPLETED" if novel_status.text.strip() == "Completed" else "ON_GOING"
            except NoSuchElementException:
                novel_status = "ON_GOING"

            meta_data.update({"description": novel_description_html, "status": novel_status})

            self.format_metadata(meta_data)

            dump_json(self.output_path, meta_data)

            print("Meta data processed successfully!")

        except Exception as e:
            logging.error(f"Failed to process metadata: {e}")
        finally:
            driver.quit()


class NovelUpdatesSource(MetadataSource):
    def __init__(self, root_path: Path, novel_name: str):
        super().__init__(root_path, novel_name)

    @property
    def base_url(self) -> Literal['https://www.novelupdates.com/series/']:
        return "https://www.novelupdates.com/series/"

    def get_metadata(self):
        driver = webdriver.Firefox()
        meta_data = {}
        try:
            driver.get(self.url)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "showtags")))

            novel_title = driver.find_element(By.CSS_SELECTOR, "div.seriestitlenu").text
            novel_author = driver.find_element(By.CSS_SELECTOR, "div#showauthors a").text
            novel_description = driver.find_element(By.CSS_SELECTOR, "div#editdescription").get_attribute("innerHTML").strip()
            novel_genres = driver.find_elements(By.CSS_SELECTOR, "div#seriesgenre a")
            novel_tags = driver.find_elements(By.CSS_SELECTOR, "div#showtags a")
            novel_status = driver.find_element(By.CSS_SELECTOR, "div#showtranslated").text.strip()
            novel_status = "ON_GOING" if novel_status == "No" else "COMPLETED"
            novel_alias = driver.find_element(By.CSS_SELECTOR, "div#editassociated").text.strip().replace("\n", ' ')

            meta_data.update(
                {
                    "title": novel_title.lower().strip(),
                    "author": novel_author.strip(),
                    "status": novel_status,
                    "description": self.clean_html(novel_description),
                    "genres": [genre.text.lower().strip() for genre in novel_genres],
                    "tags": [tag.text.lower().strip() for tag in novel_tags],
                    "alias": novel_alias,
                }
            )

            dump_json(self.output_path, meta_data)

        except Exception as e:
            logging.error(f"Failed to process metadata: {e}")
        finally:
            driver.quit()


def get_source(value: AvailableSources) -> type[WebnovelDotComSource] | type[NovelUpdatesSource] | None:
    match value:
        case AvailableSources.webnoveldotcom:
            return WebnovelDotComSource
        case AvailableSources.novelupdates:
            return NovelUpdatesSource
        

if __name__ == "__main__":
    source = NovelUpdatesSource(Path("C:/Users/bob/Desktop/NovelOutput/RenegadeImmortal/2093"), "renegade-immortal")