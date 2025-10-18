"""
This module is to be used when updating ongoing novels.
It will download, format and post the downloaded chapters to the backend.
"""

import subprocess
from pathlib import Path

import typer
from rich import print

from stalkers_cli.core import Client, Format
from stalkers_cli.utils import OUTPUT_FOLDER_NAME


def download_chapters_from_lncrawl(
    src_url: str, output_path: Path, start_index: int, end_index: int
):
    base_dir = Path(r"C:\Users\bob\desktop\lightnovel-crawler")
    venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
    lncrawl_script = base_dir / "lncrawl"

    cmd = [
        str(venv_python),
        str(lncrawl_script),
        "-s",
        src_url,
        "-o",
        str(output_path),
        "--filename_only",
        "--single",
        "--suppress",
        "--format",
        "json",
        "--close-directly",
        "--add-source-url",
        "--ignore-images",
        "--range",
        str(start_index),
        str(end_index),
    ]

    subprocess.run(cmd)


def download_format_post(response: dict, absolute_root: Path):
        novel_slug = response.get("slug")
        start_index = response.get("from")
        end_index = response.get("to")
        download_src = response.get("source")
        root_path = absolute_root / novel_slug

        download_chapters_from_lncrawl(
            src_url=download_src,
            output_path=root_path,
            start_index=start_index,
            end_index=end_index,
        )

        output_folder = root_path / OUTPUT_FOLDER_NAME

        format_updates = typer.confirm("Format updates?", default=True)
        if format_updates:
            format = Format(root_path=root_path, output_folder=output_folder)
            format.execute_range(range=(start_index, end_index))
            
            post_updates = typer.confirm("Post updates?", default=True)
            if post_updates:
                client = Client()
                client.post_chapter_in_bulk_request(chapters_file=format.output_file, novel_slug=novel_slug)


def all(responses: list[dict], absolute_root: Path):
    for index, response in enumerate(responses):
        novel_slug = response.get("slug")
        start_index = response.get("from")
        end_index = response.get("to")
        download_src = response.get("source")
        total = end_index-start_index

        download_next = typer.confirm(
            f"[{index+1}/{len(responses)}] Download updates for novel {novel_slug} from source: {download_src}?",
            default=True,
        )

        if not download_next:
            continue
        
        print(
            f"[green]Downloading updates [yellow]({start_index} ~ {end_index} [{total+1}])[/yellow] for: [/green][blue]{novel_slug}[/blue]"
        )

        download_format_post(response, absolute_root)