import logging
from pathlib import Path
from typing import Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from stalkers_cli.utils import dump_json

from .abstract_source import MetadataSource


class NovelUpdatesSource(MetadataSource):
    def __init__(self, novel_uri: str, output_folder: Path):
        super().__init__(novel_uri=novel_uri, output_folder=output_folder)

    @property
    def base_url(self) -> Literal['https://www.novelupdates.com/series/']:
        return "https://www.novelupdates.com/series/"

    def extract_metadata(self):
        logging.info("Starting metadata extraction...")

        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(options=options)
        
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
            logging.info("Finished metadata extraction...")
            driver.quit()
