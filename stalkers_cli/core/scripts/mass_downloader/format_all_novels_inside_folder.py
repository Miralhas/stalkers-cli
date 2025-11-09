from pathlib import Path
import time
from rich import print

from stalkers_cli.core import AvailableSources, Client, Format, execute_metadata_and_format, get_source
from stalkers_cli.core.metadata import MetadataSource
from stalkers_cli.utils import OUTPUT_FOLDER_NAME, dump_json

slugs = [
'return-of-the-talentless-bastard',
'summoning-players-into-my-game',
]

def get_novel_source(novel_path: Path, output_folder: Path) -> MetadataSource:
    uri_file = novel_path/"uri.txt"
    
    if not uri_file.exists():
        return get_source(AvailableSources.novelupdates)(novel_uri=novel_path.name, output_folder=output_folder)
    
    with open(uri_file) as f:
        uri = f.read().strip()
        return get_source(AvailableSources.webnoveldotcom)(novel_uri=uri, output_folder=output_folder)
    

def format_all(root_path:Path):
    requests = []
    for novel in root_path.iterdir():
        if novel.is_dir() and novel.name in slugs:
            print(f"[green]{novel.name}")
            request_status = format_and_post(novel)
            requests.append({"novel": novel.name, "status": request_status})
            time.sleep(2.5)
    
    return requests


def format_and_post(novel_path:Path):
    output_folder = novel_path / OUTPUT_FOLDER_NAME
    output_folder.mkdir(parents=True, exist_ok=True)

    format_instance = Format(root_path=novel_path, output_folder=output_folder)
    source = get_novel_source(novel_path=novel_path, output_folder=output_folder)
    
    formatted_novel = execute_metadata_and_format(source=source, format_instance=format_instance)
    novel_file = Path(f"{output_folder}/novel.json")

    dump_json(novel_file, formatted_novel)

    client = Client()
    return client.novel_request(novel_file, novel_path, True)



if __name__ == "__main__":
    root_path = Path(r"C:\Users\bob\Desktop\NovelOutput")
    format_all(root_path)
