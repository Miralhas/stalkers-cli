from enum import Enum
import logging
import time

import undetected_chromedriver as uc
from rich import print
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slugify import slugify

from stalkers_cli.core import Client

progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)

class NovelStatus(str, Enum):
    complete = "complete"
    ongoing = "ongoing"

def scrape(href: str, max: int, status: NovelStatus) -> list[dict]:
    """
    Scrape all novel slugs in a recommendation list from novelupdates.com.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--guest')
    options.set_capability('unhandledPromptBehavior', 'accept')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    driver = driver = uc.Chrome(
        use_subprocess=False,
        headless=False,
        options=options
    )
    driver.maximize_window()

    novels = []
    
    try:
        logging.info("Staring scraping...")
        driver.get(href)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.clearfix')))

        if (status == NovelStatus.complete):
            complete_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/form/div[2]/fieldset[2]/p/label[2]/input")
            complete_btn.click()
        else:
            ongoing_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/div/div[2]/form/div[2]/fieldset[2]/p/label[3]/input")
            ongoing_btn.click()

        time.sleep(2)

        while True:
            loading = driver.find_element(By.CSS_SELECTOR, "div.g_footer")
            loading.location_once_scrolled_into_view
            sections = driver.find_elements(By.CSS_SELECTOR, 'ul.clearfix li')
            if len(sections) >= max:
                break

        sections = driver.find_elements(By.CSS_SELECTOR, 'ul.clearfix li')
        
        for section in sections:
            anchor = section.find_element(By.CSS_SELECTOR, "a.c_l")
            slug = slugify(anchor.text, replacements=[["'", ""]])
            uri = anchor.get_attribute("href").split("/book/")[-1]

            novels.append({"slug": slug, "uri": uri})
    
    except Exception as ex:
        logging.error(f"Failed to extract slugs: {ex}")
    finally:
        logging.info("Finished slugs extraction...")
        driver.close()
    
    return novels


def check_slugs(novels: list[dict]) -> list[dict[str, str | bool]]:
    """
    Check each slug within the array to see if they already exist in the backend.
    """
    client = Client()
    responses = []

    with progress_bar as p:
        print("\n[bold green]Checking slugs...[/bold green]")
        for value in p.track(range(len(novels))):
            res = client.check_novel_slug(novels[value]["slug"])
            slug_exists = res.get("exists", False)
            responses.append({"slug": novels[value]["slug"], "uri":novels[value]["uri"], "onDatabase": slug_exists})
    
    return responses


def scrape_and_check_webnovel_dot_com(href: str, max: int, status: NovelStatus):
    novels = scrape(href, max=max, status=status)
    return check_slugs(novels)

if __name__ == "__main__":
    novels = scrape("https://www.webnovel.com/stories/novel", max=1000, status=NovelStatus.ongoing)
    resp = check_slugs(novels)
