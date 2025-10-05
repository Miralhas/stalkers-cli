from pathlib import Path
from time import sleep
from stalkers_cli.core import Client, Format
from stalkers_cli.utils import OUTPUT_FOLDER_NAME, timer

@timer(name="Format all")
def format_all(path: Path):
    folders = list(path.iterdir())
    print(f"Found a total of {len(folders)} novels!")
    for index, item_path in enumerate(folders):
        if item_path.is_dir():
            slug = item_path.name
            print(f"[{index+1}]: NovelOutput: {slug}")

            output_folder = Path(f"{item_path}/{OUTPUT_FOLDER_NAME}")
            output_folder.mkdir(parents=True, exist_ok=True)
            
            format = Format(root_path=item_path, output_folder=output_folder)
            format.execute()
            
            client = Client()
            client.put_chapter_in_bulk_request(chapters_file=format.output_file, novel_slug=slug)
            sleep(5)


if __name__ == "__main__":
    format_all(Path(r"C:\Users\bob\Desktop\NovelOutput"))
