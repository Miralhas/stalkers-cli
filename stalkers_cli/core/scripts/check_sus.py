from pathlib import Path
from stalkers_cli.utils import timer
from rich import print

def check_if_downloaded(novel_path: Path):
    cover = novel_path / "cover.jpg"
    json_folder = novel_path / "json"
    return cover.exists(follow_symlinks=False) and json_folder.exists(follow_symlinks=False)


def sus_chapters(novel_path: Path):
    json_folder = novel_path / "json"
    total_sus = 0
    for chapter_file in json_folder.glob("*.json"):
        file_size_kb = chapter_file.stat().st_size / 1024
        if file_size_kb < 1.5:
            total_sus += 1
    
    return total_sus


@timer(name="Checking for SUS chapters")
def check_sus(novelOutput: Path):
    folders = list(novelOutput.iterdir())
    print(f"Found a total of {len(folders)} novels!")
    sus_folders = []
    for index, item_path in enumerate(folders):
        if item_path.is_dir():
            if check_if_downloaded(item_path):
                total_sus = sus_chapters(item_path)
                if total_sus > 0:
                    print(f"[{index+1}]: [cyan]{item_path.name}[/cyan] - [red]{total_sus} SUS chapters![/red]")
                    sus_folders.append({"name":item_path.name, "reason": f"{total_sus} SUS chapters!", "path": item_path})

                else:
                    print(f"[{index+1}]: [cyan]{item_path.name}[/cyan] [green]is clean[/green]")

            else:
                print(f"[{index+1}]: [cyan]{item_path.name}[/cyan] - [red]FAILED TO DOWNLOAD![/red]")
                sus_folders.append({"name":item_path.name, "reason": f"FAILED TO DOWNLOAD!", "path": item_path})
    
    return sus_folders


if __name__ == "__main__":
    check_sus(Path(r"C:\Users\bob\Desktop\rec_lists\antihero_122327"))
