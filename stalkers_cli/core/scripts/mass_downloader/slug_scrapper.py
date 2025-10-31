import logging
from pathlib import Path

import undetected_chromedriver as uc
from rich import print
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn)
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

def get_link(base_link:str, start_page: int):
    if ("?" in base_link):
        return f"{base_link}&pg={start_page}"

    return f"{base_link}?pg={start_page}"


def scrape(req_list_url: str, end_page: int | None = None, start_page=1) -> list[str]:
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
    driver = uc.Chrome(
        use_subprocess=False,
        headless=False,
        options=options
    )
    driver.maximize_window()

    slugs = []
    
    current_page = start_page

    try:
        logging.info("Starting slugs extraction...")
        driver.get(get_link(req_list_url, start_page))
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="unic-b"]/div/div/div/div[3]/div[1]/button[2]')))
        driver.find_element(By.XPATH, '//*[@id="unic-b"]/div/div/div/div[3]/div[1]/button[2]').click()

        while True:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.w-blog-content")))
                
                novels_containers = driver.find_elements(By.CSS_SELECTOR, "div.search_main_box_nu")
                for container in novels_containers:
                    a_tag = container.find_element(By.CSS_SELECTOR, "a")
                    slug = a_tag.get_attribute("href").removesuffix("/").split("/")[-1]
                    slugs.append(slug)
                
                next_page_btn = driver.find_element(By.CSS_SELECTOR, "a.next_page")
                next_page_btn.click()
                current_page += 1
            except NoSuchElementException:
                break
            
            if (end_page is not None and current_page > end_page):
                break
        
    except Exception as ex:
        logging.error(f"Failed to extract slugs: {ex}")
    finally:
        logging.info("Finished slugs extraction...")
        driver.close()
    
    return slugs


def check_slugs(slugs: list[str]) -> list[dict[str, str | bool]]:
    """
    Check each slug within the array to see if they already exist in the backend.
    """
    client = Client()
    responses = []

    with progress_bar as p:
        print("\n[bold green]Checking slugs...[/bold green]")
        for value in p.track(range(len(slugs))):
            res = client.check_novel_slug(slugs[value])
            slug_exists = res.get("exists", False)
            responses.append({"slug": slugs[value], "onDatabase": slug_exists})
    
    return responses


def scrape_and_check(req_list_url: str, end_page: int | None = None, start_page=1):
    slugs = scrape(req_list_url, start_page=start_page, end_page=end_page)
    return check_slugs(slugs)

if __name__ == "__main__":
    # slugs = scrape("https://www.novelupdates.com/series-ranking/", end_page=4)
    # print(len(slugs))
    path = Path(r"C:\Users\bob\Desktop\NovelOutput")
    slugs = []
    for novel in path.iterdir():
        if novel.is_dir():
            slugs.append(novel.name)
    
    res = check_slugs(slugs)
    
    print([notOnDB for notOnDB in res if notOnDB["onDatabase"]==False])