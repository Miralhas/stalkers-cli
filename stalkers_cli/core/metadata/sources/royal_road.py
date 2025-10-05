import logging
from pathlib import Path
from typing import Literal

from rich import print
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from stalkers_cli.utils import dump_json

from .abstract_source import MetadataSource
from .constants import GENRES


class RoyalRoadSource(MetadataSource):
    def __init__(self, novel_uri: str, output_folder: Path):
        super().__init__(novel_uri=novel_uri, output_folder=output_folder)

    @property
    def base_url(self) -> Literal["https://www.royalroad.com/fiction/"]:
        return "https://www.royalroad.com/fiction/"
    
    def extract_metadata(self):
        logging.info("Starting metadata extraction...")
        driver = webdriver.Firefox()
        metadata = {}

        try:
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)

            # Main container
            wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div/div/div[1]/div")))

            raw_description = driver.find_element(By.CSS_SELECTOR, "div.hidden-content").get_attribute("innerHTML").strip()
            description = self.clean_html(raw_description)

            raw_status = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/span[2]").text.strip()
            status = "COMPLETED" if raw_status == "COMPLETED" else "ON_GOING"

            title = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div/h1").text

            author = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[1]/div/div[1]/div[2]/div/h4/span[2]/a").text

            description = self.clean_html(raw_description)

            status = "COMPLETED" if raw_status == "COMPLETED" else "ON_GOING"

            try:
                # To show all tags, it's needed to click this button
                show_tags_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/span[3]/label")
                show_tags_button.click()
            except Exception as e:
                print(e)

            tags_container = driver.find_elements(By.CSS_SELECTOR, "a.fiction-tag")

            tags = []
            genres = []

            for tag_element in tags_container:
                tag = tag_element.text.lower().strip()
                if (tag in GENRES):
                    genres.append(tag)
                else:
                    tags.append(tag)
            
            metadata.update({
                "title": title.lower().strip(),
                "author": author.strip(),
                "status": status,
                "description": description,
                "genres": genres,
                "tags": tags,
            })

            dump_json(self.output_path, metadata)

        except Exception as e:
            logging.error(f"Failed to process metadata: {e}")
        finally:
            logging.info("Finished metadata extraction...")
            driver.quit()