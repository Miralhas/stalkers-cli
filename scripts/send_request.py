import json
import os
import time
from pathlib import Path
from typing import Dict

import requests
from dotenv import dotenv_values, load_dotenv
from rich import print

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
ROBOT_HEADER = os.getenv("ROBOT_HEADER")
ROBOT_SECRET = os.getenv("ROBOT_SECRET")

required_keys = ["BASE_URL", "ROBOT_HEADER", "ROBOT_SECRET"]
missing_keys = [key for key in required_keys if key not in dotenv_values(".env")]

if missing_keys:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_keys)}. "
        "Please ensure these keys are set in the .env file."
    )

# assert BASE_URL is not None and ROBOT_HEADER is not None and ROBOT_SECRET is not None, "Missing or invalid environment variables. Please ensure all required keys are correctly set in the .env file."
# assert ROBOT_HEADER is not None, "Load a .env file"
# assert ROBOT_SECRET is not None, "Load a .env file"

def load_json(file_path: Path) -> Dict:
    """Load JSON data from a file."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON from {file_path}: {e}") from e
    

def post_novel(novel_path: Path) -> requests.Response:
    data = load_json(novel_path)
    url = f"{BASE_URL}/api/novels"
    
    headers = {
        ROBOT_HEADER: ROBOT_SECRET,
        "Content-Type": "application/json",
    }

    print(f"Sending novel POST request to '{url}'")

    start = time.time()
    r = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
    end = time.time()
    
    length = end - start
    print(f"Post REQUEST took: {length:.2f} seconds")
    return r


def put_novel_image(root_path: Path, novel_slug: str) -> requests.Response:
    headers = {
        ROBOT_HEADER: ROBOT_SECRET,
    }
    url = f"{BASE_URL}/api/novels/{novel_slug}/image"

    image_path = f"{root_path}/cover.jpg"
    files = [
        ('file',(f'{novel_slug}_cover.jpeg', open(image_path, 'rb'),'image/jpeg'))
    ]

    payload = {'description': f'{novel_slug} cover'}
    
    print(f"Sending image PUT request to '{url}'")
    r = requests.put(url, headers=headers, files=files, data=payload, timeout=30)
    print(r.json())


def post_novel_chapters(novel_path: Path, novel_slug: str):
    data = load_json(novel_path)
    url = f"{BASE_URL}/api/novels/{novel_slug}/chapters/save-bulk"
    
    headers = {
        ROBOT_HEADER: ROBOT_SECRET,
        "Content-Type": "application/json",
    }

    print(f"Sending novel POST request to '{url}'")
    r = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)

    return r


def bulk_chapters_request(root_path: Path, novel_slug):
    novel_path = Path(f"{root_path}/formatted-novel/novel.json")
    try:
        r = post_novel_chapters(novel_path=novel_path, novel_slug=novel_slug)
        r.raise_for_status()
        print(f"Request was successful!")
    except requests.HTTPError as ex:
        print(f"Failed with a response code of '{r.status_code}'! \n{r.json()}")
    except requests.Timeout:
        print("Faile because request timed out!")
    except Exception as e:
        print(f"Erro ao fazer requisição! \n{e}")


def novel_request(with_image: bool, root_path: Path):
    novel_path = Path(f"{root_path}/formatted-novel/novel.json")
    try:
        r = post_novel(novel_path=novel_path)
        r.raise_for_status()

        print(f"Request was successful! \n{r.json()}")

        novel_info: Dict = r.json()

        if (with_image):
            put_novel_image(root_path, novel_slug=novel_info["slug"])

    except requests.HTTPError as ex:
        print(f"Failed with a response code of '{r.status_code}'! \n{r.json()}")
    except requests.Timeout:
        print("Faile because request timed out!")
    except Exception as e:
        print(f"Erro ao fazer requisição! \n{e}")


if __name__ == "__main__":
    put_novel_image(Path("C:/Users/bob/Desktop/NovelOutput/RenegadeImmortal/"), "renegade-immortal")
    pass
