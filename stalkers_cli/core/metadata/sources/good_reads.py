import logging
from pathlib import Path
from typing import ClassVar, List, Literal

from rich import print
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from stalkers_cli.core.metadata.sources.abstract_source import MetadataSource
from stalkers_cli.core.metadata.sources.constants import GENRES
from stalkers_cli.utils import dump_json, load_json


class GoodReadsSource(MetadataSource):
    blacklisted_genres: ClassVar[list[str]]
    tags_mapper: ClassVar[list[dict]]

    def __init__(self, novel_uri: str, output_folder: Path):
        super().__init__(novel_uri=novel_uri, output_folder=output_folder)
        self.blacklisted_genres = load_json(Path("stalkers_cli/utils/goodreads_tags_map.json"))["blacklist"]
        self.tags_mapper = load_json(Path("stalkers_cli/utils/goodreads_tags_map.json"))["mapper"]
        

    @property
    def base_url(self) -> Literal["https://www.goodreads.com/book/show/"]:
        return "https://www.goodreads.com/book/show/"
    
    def format_metadata(self, metadata_dict: dict):
        """formats given dict to stalkers-api standards
        Args:
            metadata_dict (Dict): dict containing metadata retrieved through selenium
        """
        genres_and_tags = metadata_dict["genres_and_tags"]
        
        genres_and_tags = [genre for genre in genres_and_tags if genre not in self.blacklisted_genres]
        genres_and_tags = [self.tags_mapper[genre] if genre in self.tags_mapper.keys() else genre for genre in genres_and_tags]

        genres = [genre for genre in genres_and_tags if genre in GENRES]
        genres.append("book")

        metadata_dict["genres"] = genres
        metadata_dict["tags"] = genres_and_tags

        del metadata_dict["genres_and_tags"]

    def extract_metadata(self):
        logging.info("Starting metadata extraction...")

        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(options=options)
        
        meta_data = {}
        try:
            driver.get(self.url)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.BookPage__mainContent")))

            try:
                show_all_genres_btn = driver.find_element(By.CSS_SELECTOR, "div.BookPageMetadataSection__genres div.Button__container button")
                show_all_genres_btn.click()
            except NoSuchElementException:
                print("no show more")
                pass

            title = driver.find_element(By.CSS_SELECTOR, "div.BookPageTitleSection__title h1").text
            author = driver.find_element(By.CSS_SELECTOR, "span.ContributorLink__name").text
            description = driver.find_element(By.CSS_SELECTOR, "div.DetailsLayoutRightParagraph__widthConstrained span").get_attribute("outerHTML").strip()
            genres_container = driver.find_elements(By.CSS_SELECTOR, "span.BookPageMetadataSection__genreButton a span")
            genres_and_tags = [genre.text.strip().lower() for genre in genres_container]
            status = "COMPLETED"

            meta_data.update(
                {
                    "title": title.lower().strip(),
                    "author": author.strip(),
                    "status": status,
                    "description": self.clean_html(description),
                    "genres_and_tags": genres_and_tags,
                }
            )

            try:
                alias = driver.find_element(By.CSS_SELECTOR, "div.BookPageTitleSection__title h3").text
                meta_data.update({ "alias": alias })
            except NoSuchElementException:
                pass

            self.format_metadata(metadata_dict=meta_data)

            dump_json(self.output_path, meta_data)

        except Exception as e:
            logging.error(f"Failed to process metadata: {e}")
        finally:
            logging.info("Finished metadata extraction...")
            driver.quit()


if __name__ == "__main__":
    src = GoodReadsSource(
        novel_uri="41886271-the-sword-of-kaigen", 
        output_folder=Path(r"C:\Users\bob\Desktop\the-sword-of-kaigen\formatted-novel")
    )

    src.extract_metadata()