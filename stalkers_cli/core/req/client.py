import json
import logging
import os
from pathlib import Path
from typing import ClassVar, Dict, List

import requests
from dotenv import load_dotenv
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from utils import load_json, timer

logging.basicConfig(level=logging.INFO)

load_dotenv()
BASE_URL = os.getenv("BASE_URL")
ROBOT_HEADER = os.getenv("ROBOT_HEADER")
ROBOT_SECRET = os.getenv("ROBOT_SECRET")

assert BASE_URL is not None, "BASE_URL missing from .env file"
assert ROBOT_HEADER is not None, "ROBOT_HEADER missing from .env file"
assert ROBOT_SECRET is not None, "ROBOT_SECRET a missing from .env file"

class Client():
    base_url: ClassVar[str]
    base_headers: ClassVar[Dict[str, str]]

    def __init__(self):
        self.base_url = BASE_URL
        self.base_headers = {ROBOT_HEADER: ROBOT_SECRET}
        

    @timer(name="POST Novel")
    def __post_novel(self, novel_file: Path):
        data = load_json(novel_file)
        url = f"{self.base_url}/novels"
        headers = {
            ROBOT_HEADER: ROBOT_SECRET,
            "Content-Type": "application/json",
        }

        logging.info(f"Sending novel POST request to '{url}'")

        with Progress( SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Posting Novel...", total=None)
            return requests.post(url=url, headers=headers, data=json.dumps(data), timeout=30)
    

    @timer(name="PUT Novel Cover")
    def __put_cover(self, novel_slug: str, root_path: Path):
        url = f"{self.base_url}/novels/{novel_slug}/image"
        image_path = f"{root_path}/cover.jpg"

        files = [
            ('file',(f'{novel_slug}_cover.jpeg', open(image_path, 'rb'),'image/jpeg'))
        ]
        payload = {'description': f'{novel_slug} cover'}

        return requests.put(url, headers = {ROBOT_HEADER: ROBOT_SECRET}, files=files, data=payload, timeout=30)


    @timer(name="PUT Chapters in Bulk")
    def __put_chapters_bulk(self, chapters_file: Path, novel_slug:str):
        data: List[Dict] = load_json(chapters_file)
        data_dict = {"chapters": data}
        url = f"{self.base_url}/novels/{novel_slug}/chapters/save-bulk"
        headers = {
            ROBOT_HEADER: ROBOT_SECRET,
            "Content-Type": "application/json",
        }

        logging.info(f"Sending novel POST request to '{url}'")

        with Progress( SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Posting Chapters in Bulk...", total=None)
            return requests.post(url=url, headers=headers, data=json.dumps(data_dict), timeout=30)

    def bulk_chapters_request(self, chapters_file:Path, novel_slug:str):        
        try:        
            if not chapters_file.exists():
                raise Exception(f"Chapters file {chapters_file} doesn't exist")
            
            r = self.__put_chapters_bulk(chapters_file=chapters_file, novel_slug=novel_slug)
            r.raise_for_status()

            print(f"[green]Request was successful![/green]")

        except requests.HTTPError as ex:
            print(f"[bold red]Failed with a response code of [italic red]'{r.status_code}'[/italic red]![/bold red] [red]\n{r.json()}[/red]")
        except requests.Timeout:
            print("[bold red]Faile because request timed out![/bold red]")
        except Exception as e:
            print(f"[bold red]Something went wrong![/bold red] \n[red]{e}[/red]")


    def novel_request(self, novel_file: Path, root_path:Path, with_image: bool):        
        try:
            if not novel_file.exists():
                raise Exception(f"Novel file {novel_file} doesn't exist")
            r = self.__post_novel(novel_file)
            r.raise_for_status()

            print(f"{r.json()}")

            novel_info: Dict = r.json()

            if (with_image):
                r = self.__put_cover(root_path=root_path, novel_slug=novel_info["slug"])
                r.raise_for_status()

        except requests.HTTPError as ex:
            print(f"[bold red]Failed with a response code of [italic red]'{r.status_code}'[/italic red]![/bold red] [red]\n{r.json()}[/red]")
        except requests.Timeout:
            print("[bold red]Faile because request timed out![/bold red]")
        except Exception as e:
            print(f"[bold red]Something went wrong![/bold red] \n[red]{e}[/red]")
        