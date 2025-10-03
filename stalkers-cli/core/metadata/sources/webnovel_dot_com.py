import logging
from pathlib import Path
from typing import List, Literal

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import dump_json

from .abstract_source import MetadataSource
from .constants import GENRES


class WebnovelDotComSource(MetadataSource):
    def __init__(self, novel_uri: str, output_folder: Path):
        super().__init__(novel_uri=novel_uri, output_folder=output_folder)
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
            genre for genre in GENRES if genre.lower().strip() in tags
        ]

        metadata_dict["tags"] = tags
        del metadata_dict["tag"]

        metadata_dict["title"] = metadata_dict["title"].lower()

    def extract_metadata(self):
        logging.info("Starting metadata extraction...")
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
            logging.info("Finished metadata extraction...")
            driver.quit()
