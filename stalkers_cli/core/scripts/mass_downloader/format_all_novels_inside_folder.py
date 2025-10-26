from genericpath import isdir
from pathlib import Path
import time
from rich import print

from stalkers_cli.core import AvailableSources, Client, Format, execute_metadata_and_format, get_source
from stalkers_cli.utils import OUTPUT_FOLDER_NAME, dump_json, open_in_file_explorer
import typer

def format_all(root_path:Path):
    requests = []
    for novel in root_path.iterdir():
        if novel.is_dir():
            request_status = format_and_post(novel)
            requests.append({"novel": novel.name, "status": request_status})
            time.sleep(5)
    
    return requests


def format_and_post(novel_path:Path):
    output_folder = novel_path / OUTPUT_FOLDER_NAME
    output_folder.mkdir(parents=True, exist_ok=True)

    format_instance = Format(root_path=novel_path, output_folder=output_folder)
    source = get_source(value=AvailableSources.novelupdates)(novel_uri=novel_path.name, output_folder=output_folder)
    
    formatted_novel = execute_metadata_and_format(source=source, format_instance=format_instance)
    novel_file = Path(f"{output_folder}/novel.json")

    dump_json(novel_file, formatted_novel)
    # open_in_file_explorer(format_instance.output_folder)

    # post_updates = typer.confirm("Post updates?", default=True)
    # if post_updates:
    client = Client()
    return client.novel_request(novel_file, novel_path, True)


if __name__ == "__main__":
    root_path = Path(r"C:\Users\bob\Desktop\rec_lists\antihero_122327")
    format_all(root_path)
