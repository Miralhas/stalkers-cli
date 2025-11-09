import logging
import time
from pathlib import Path

import undetected_chromedriver as uc
from rich import print
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn)
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
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

def scrape(href: str, max: int) -> list[dict]:
    """
    Scrape all novel slugs in a recommendation list from novelupdates.com.
    """
    options = Options()
    options.set_preference("intl.accept_languages", "en-US")
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    novels = []
    
    try:
        logging.info("Staring scraping...")
        driver.get(href)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[2]/div[4]')))

        while True:
            loading = driver.find_element(By.CSS_SELECTOR, "div.g_loading")
            loading.location_once_scrolled_into_view
            sections = driver.find_elements(By.CSS_SELECTOR, "section.df.g_hr.pt16.pb16")
            if len(sections) >= max:
                break
            time.sleep(1)

        sections = driver.find_elements(By.CSS_SELECTOR, "section.df.g_hr.pt16.pb16")
        
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


def scrape_and_check_webnovel_dot_com_ranking(href: str, max: int):
    novels = scrape(href, max=max)
    return check_slugs(novels)

if __name__ == "__main__":
    novels = scrape("https://www.webnovel.com/ranking/novel/all_time/power_rank", max=100)
    resp = check_slugs(novels)
