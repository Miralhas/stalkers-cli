import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import questionary
from questionary import Choice
from rich import print
from rich.console import Console
from rich.progress import (BarColumn, MofNCompleteColumn, Progress, TextColumn,
                           TimeElapsedColumn, TimeRemainingColumn)
from rich.table import Table

from stalkers_cli.core.scripts.mass_downloader.slug_scrapper import \
    scrape_and_check

AVAILABLE_SOURCES = [
    # {"name": "novlove.com", "src": "https://novlove.com/novel", "hasHtmlSuffix": False},
    {"name": "novelfull.me", "src": "https://novelfull.me", "hasHtmlSuffix": False},
    {"name": "novelnext.com", "src": "https://novelnext.com/books", "hasHtmlSuffix": False},
    {"name": "wuxia.city", "src": "https://wuxia.city/book", "hasHtmlSuffix": False},
    {"name": "wuxia.click", "src": "https://wuxia.click/novel", "hasHtmlSuffix": False},
    {"name": "novels.pl", "src": "https://www.novels.pl/novel", "hasHtmlSuffix": False},
    {"name": "novgo.net", "src": "https://novgo.net", "hasHtmlSuffix": True},
    {"name": "www.allnovel.org", "src": "https://www.allnovel.org", "hasHtmlSuffix": True},
    {"name": "allnovel.org", "src": "https://allnovel.org", "hasHtmlSuffix": True},
    {"name": "allnovelfull.net", "src": "https://allnovelfull.net", "hasHtmlSuffix": True},
    {"name": "allnovelfull.com", "src": "https://allnovelfull.com", "hasHtmlSuffix": True},
]

progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)


def print_table(responses: list[dict]):
    """
    Responses array to rich table.
    """
    if not responses:
        print("[bold red]No responses to display.[/bold red]")
        return

    console = Console()

    table = Table(
        title=f"Novels to download [{len(responses)}]",
        show_lines=True,
        header_style="bold green",
        width=60
    )

    table.add_column("Slug", style="green")
    table.add_column("On Database", style="yellow")

    for res in responses:
        table.add_row(
            res.get("slug", ""),
            str(res.get("onDatabase", False)),
        )

    console.print(table)



def slug_to_sources(slug: str) -> list[dict]:
    download_sources = []
    for source in AVAILABLE_SOURCES:
        formatted_source = {
            "name": source["name"],
            "src": f"{source["src"]}/{slug}",
            "slug": slug,
        }
        if source["hasHtmlSuffix"]:
            formatted_source["src"] += ".html"

        download_sources.append(formatted_source)
    return download_sources


def get_downloadable_source(sources: list[dict]):
    best_source = None
    most_chapters = 0

    for source in sources:
        base_dir = Path(r"C:\Users\bob\desktop\lightnovel-crawler")
        venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
        lncrawl_script = base_dir / "lncrawl"

        cmd = [str(venv_python), str(lncrawl_script), "-s", source["src"]]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        output = result.stdout + result.stderr

        match = re.search(r"(\d+)\s+chapters\s+found", output)

        if match:
            total_chapters = int(match.group(1))
            print(
                f"Source [blue]{source["name"]}[/blue] has the novel {source["slug"]} in its catalog with {total_chapters} chapters to download"
            )
            source["chapters"] = total_chapters
            if total_chapters >= most_chapters:
                most_chapters = total_chapters
                best_source = source
    
    return best_source
            


def execute_lncrawl(source: dict, output_path: Path):
    base_dir = Path(r"C:\Users\bob\desktop\lightnovel-crawler")
    venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
    lncrawl_script = base_dir / "lncrawl"

    cmd = [
        str(venv_python),
        str(lncrawl_script),
        "-s",
        source["src"],
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
        "--all",
    ]

    subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)


def download_single_novel(novel, root_path: Path):
    try:
        sources = slug_to_sources(novel["slug"])
        source = get_downloadable_source(sources)
        if source is not None:
            output_path = root_path / source["slug"]
            execute_lncrawl(source, output_path)
            return {
                "slug": source["slug"],
                "status": "SUCCESS",
                "message": "Downloaded successfully! [Needs to be checked!]",
                "src": source["src"],
                "chapters": source["chapters"]
            }
        else:
            slug = novel.get("slug", "unknown")
            print(f"[red]Couldn't find source for novel {slug}[/red]")
            return {
                "slug": slug,
                "status": "ERROR",
                "message": "Not found in sources."
            }
    except Exception as e:
        return {
            "slug": novel.get("slug", "unknown"),
            "status": "ERROR",
            "message": f"Exception: {e}"
        }


def download_rec_list(rec_list_link: str, root_path: Path, max_workers: int = 5) -> list[dict]:
    responses = []

    novels = sorted(scrape_and_check(rec_list_link), key=lambda novel: novel["slug"])

    novels_to_download = questionary.checkbox(
        f"\n\nNovels to be downloaded [{len(novels)}]",
        choices=[Choice(title=novel["slug"], value=novel, checked=True) for novel in novels if novel["onDatabase"] == False],
    ).ask()

    print_table(novels_to_download)

    with progress_bar as p:
        task1 = p.add_task("[red]Downloading...", total=len(novels_to_download))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_single_novel, novel, root_path): novel for novel in novels_to_download}

            for future in as_completed(futures):
                p.update(task1, advance=1)
                result = future.result()
                responses.append(result)

    print("\n[bold green]All downloads completed![/bold green]")
    return responses


if __name__ == "__main__":
    root_path = Path(r"C:\Users\bob\Desktop\rec_lists\a_list_8211")
    responses = download_rec_list("https://www.novelupdates.com/viewlist/8211/", root_path, max_workers=5)


    