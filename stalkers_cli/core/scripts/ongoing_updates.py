"""
This script automates the process of checking ongoing web novels for new chapters.
Create an Excel report at C:\\Users\\bob\\Desktop\\On Going Updates
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from rich import print
from rich.pretty import pprint

from stalkers_cli.core import Client, Format
from stalkers_cli.utils import load_json

MISMATCH_ERROR_MESSAGE = "Negative chapters to download. Source is mismatched!"
SOURCE_NONE_MESSAGE = "Source is None"
UP_TO_DATE_MESSAGE = "Novel is up to date"
NOVELS_STORAGE_PATH = Path(r"C:\Users\bob\Desktop\NovelOutput")
XLSX_OUTPUT_PATH = Path(r"C:\Users\bob\Desktop\On Going Updates")


def get_novel_source_from_chapter_slug(slug: str, absolute_root: Path):
    """
    Gets the download source of a novel
    """
    novel_dir = absolute_root / slug
    meta_json_file = novel_dir / "meta.json"

    if not meta_json_file.exists():
        return None

    return load_json(meta_json_file).get("novel").get("url")


def get_novel_chapters_count_from_source(src_url: str):
    """
    Runs LightNovel Crawler via subprocess to retrieve total chapter count from a source URL.
    """
    base_dir = Path(r"C:\Users\bob\desktop\lightnovel-crawler")
    venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
    lncrawl_script = base_dir / "lncrawl"

    cmd = [str(venv_python), str(lncrawl_script), "-s", src_url]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
    output = result.stdout + result.stderr

    match = re.search(r"(\d+)\s+chapters\s+found", output)

    if match:
        return int(match.group(1))
    else:
        raise ValueError("Could not extract chapter count from output.")


def build_response(
    slug: str,
    type_: str,
    message: str,
    source_url: Optional[str] = None,
    chapters_to_download: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Helper to build response objects.
    """
    response = {"slug": slug, "type": type_, "message": message}
    if source_url:
        response["source_url"] = source_url
    if chapters_to_download:
        response["chapters_to_download"] = chapters_to_download
    return response


def get_responses(novels: list[dict], absolute_root: Path):
    """
    For each novel, check if new chapters are available and return structured responses.
    """
    responses = []
    print(f"[green]Checking a total of:[/green] [blue]{len(novels)}[/blue] [green]novels[/green]")
    for novel in novels:
        title = novel.get("title")
        slug = novel.get("slug")

        print(f"[green]Checking novel:[/green] [blue]{title}[/blue]")

        src = get_novel_source_from_chapter_slug(slug, absolute_root)

        if not src:
            responses.append({"slug": slug, "type": "ERROR", "message": SOURCE_NONE_MESSAGE})
            continue

        try:
            chapters_on_source = get_novel_chapters_count_from_source(src)
            chapters_on_db = novel.get("chaptersCount")
            chapters_to_download = chapters_on_source - chapters_on_db

            if chapters_to_download > 0:
                responses.append({
                    "slug": slug,
                    "type": "SUCCESS",
                    "message": f"There are {chapters_to_download} new chapters to download",
                    "source": src,
                    "chapters_count": chapters_on_db,
                    "from": chapters_on_db+1,
                    "to": chapters_on_db+chapters_to_download,
                })
            elif chapters_to_download < 0:
                responses.append(
                    {"slug": slug, "type": "ERROR", "message": MISMATCH_ERROR_MESSAGE}
                )
            else:
                responses.append(
                    {"slug": slug, "type": "NO_UPDATE", "message": UP_TO_DATE_MESSAGE, "chapters_count": chapters_on_db,}
                )

        except ValueError as ex:
            responses.append({"slug": slug, "type": "ERROR", "message": str(ex)})

    return responses


def responses_to_xlsx(responses: list[dict]):
    """ "
    Will create a xlsx report with the data on the responses array.
    """
    if not responses:
        raise Exception("Responses is invalid!")

    XLSX_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = XLSX_OUTPUT_PATH / f"novels_to_update-{timestamp}.xlsx"

    df = pd.DataFrame(responses)

    print("Saving responses to excel")

    df.to_excel(filename, index=False, engine="openpyxl")


def execute_ongoing_updates(absolute_root: Path):
    """
    Will fetch all ongoing novels from the backend, verify if there are new chapters to download
    and create a xlsx report.
    """
    client = Client()
    novels = client.get_all_ongoing_novels_info()
    responses = get_responses(novels, absolute_root)
    responses_to_xlsx(responses)
    return responses


if __name__ == "__main__":
    execute_ongoing_updates()
