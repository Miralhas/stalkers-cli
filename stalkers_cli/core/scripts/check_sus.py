from pathlib import Path
from stalkers_cli.core import Format
from stalkers_cli.utils import OUTPUT_FOLDER_NAME, timer
from rich import print

@timer(name="Checking for SUS chapters")
def check_sus(novelOutput: Path):
    folders = list(novelOutput.iterdir())
    print(f"Found a total of {len(folders)} novels!")
    for index, item_path in enumerate(folders):
        if item_path.is_dir():
            print(f"[{index+1}]: Checking: [green]{item_path.name}[/green]")
            output_folder = Path(f"{item_path}/{OUTPUT_FOLDER_NAME}")
            output_folder.mkdir(parents=True, exist_ok=True)

            format = Format(item_path, output_folder)
            format.validate()

if __name__ == "__main__":
    check_sus(Path(r"C:\Users\bob\Desktop\NovelOutput"))
