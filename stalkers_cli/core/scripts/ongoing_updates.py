"""
This script automates the process of checking ongoing web novels for new chapters.
Create an Excel report at C:\\Users\\bob\\Desktop\\On Going Updates
"""

import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Optional

from rich import print

from stalkers_cli.core import Client
from stalkers_cli.utils import load_json, dict_to_xlsx, timer

MISMATCH_ERROR_MESSAGE = "Negative chapters to download. Source is mismatched!"
NOVEL_NOT_STORED_LOCALLY = "Nove is not stored locally!"
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


def get_response(novel: list[dict], absolute_root: Path, index: int):
    title = novel.get("title")
    slug = novel.get("slug")

    absolute_root_novels_slugs = [novel_path.name for novel_path in list(absolute_root.iterdir()) if novel_path.is_dir()]

    if slug not in absolute_root_novels_slugs:
        return {"slug": slug, "type": "ERROR", "message": NOVEL_NOT_STORED_LOCALLY}

    print(f"[green][{index+1}] Checking novel:[/green] [yellow]{title}[/yellow]")

    src = get_novel_source_from_chapter_slug(slug, absolute_root)

    if not src:
        return {"slug": slug, "type": "ERROR", "message": SOURCE_NONE_MESSAGE}

    try:
        chapters_on_source = get_novel_chapters_count_from_source(src)
        chapters_on_db = novel.get("chaptersCount")
        chapters_to_download = chapters_on_source - chapters_on_db

        if chapters_to_download > 0:
            return {
                "slug": slug,
                "type": "SUCCESS",
                "message": f"There are {chapters_to_download} new chapters to download",
                "source": src,
                "chapters_count": chapters_on_db,
                "from": chapters_on_db+1,
                "to": chapters_on_db+chapters_to_download,
            }
        elif chapters_to_download < 0:
            return {"slug": slug, "type": "ERROR", "message": MISMATCH_ERROR_MESSAGE}
            
        else:
            return {"slug": slug, "type": "NO_UPDATE", "message": UP_TO_DATE_MESSAGE, "chapters_count": chapters_on_db}

    except ValueError as ex:
        return {"slug": slug, "type": "ERROR", "message": str(ex)}


def get_responses(novels: list[dict], absolute_root: Path, workers: int):
    """
    For each novel, check if new chapters are available and return structured responses.
    """
    responses = []
    print(f"[green]Checking a total of:[/green] [yellow]{len(novels)}[/yellow] [green]novels[/green]")

    with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(get_response, novel, absolute_root, index): novel for index, novel in enumerate(novels)}

            for future in as_completed(futures):
                result = future.result()
                responses.append(result)
    
    return sorted(responses, key=lambda response: response["slug"])


@timer("Updates Check")
def execute_ongoing_updates(absolute_root: Path, workers: int):
    """
    Will fetch all ongoing novels from the backend, verify if there are new chapters to download
    and create a xlsx report.
    """
    client = Client()
    novels = client.get_all_ongoing_novels_info()
    responses = get_responses(novels, absolute_root, workers)
    dict_to_xlsx(responses, XLSX_OUTPUT_PATH, "updates_report")
    return responses


if __name__ == "__main__":
    execute_ongoing_updates()
