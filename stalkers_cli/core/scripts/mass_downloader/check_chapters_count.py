import re
import subprocess
from pathlib import Path

from stalkers_cli.core import Client
from stalkers_cli.utils import load_json
from rich import print


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
    

def downloaded_chapters_count(novel_path: Path) -> int:
    json_dir = novel_path / "json"
    return len(list(json_dir.iterdir()))


def all_novels(root_path:Path):
    for novel in root_path.iterdir():
        if novel.is_dir():
            novel_dict = load_json(novel/"meta.json")
            url = novel_dict.get("novel").get("url")
            if url is not None:
                source_chapters = get_novel_chapters_count_from_source(url)
                downloaded_count = downloaded_chapters_count(novel)
                if (downloaded_count != source_chapters):
                    print(f"[red]Chapters mismatch: {novel.name}")
                else:
                    print(f"[green]Novel {novel.name} downloaded successfully!")


# def check_if_downloaded(root_path: Path):
#     for novel in root_path.iterdir():
#         if novel.is_dir():
#             cover_exists = (novel/"cover.jpg").exists()
#             if cover_exists:
#                 print(f"[green]Novel {novel.name} downloaded successfully!")
#             else:
#                 print(f"[red]Novel {novel.name} failed to download!")

def check_if_downloaded(root_path: Path):
    for novel in root_path.iterdir():
        if novel.is_dir():
            client = Client()
            res = client.check_novel_slug(novel.name)
            slug_exists = res.get("exists", False)
            print(f"[yellow]{novel.name}:[/yellow] {slug_exists}")



if __name__ == "__main__":
    root_path = Path(r"C:\Users\bob\Desktop\rec_lists\antihero_122327")
    all_novels(root_path)