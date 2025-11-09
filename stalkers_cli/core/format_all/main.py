from ast import Dict, dump
from pathlib import Path
from typing import List

from stalkers_cli.core.format import Format
from stalkers_cli.core.metadata import MetadataSource
from stalkers_cli.utils import load_json, dump_json


def execute_metadata_and_format(source: MetadataSource, format_instance: Format) -> Dict:
    """
    Executes both format and metadata extraction scripts and fuses them toghether in a json file.
    """
    source.extract_metadata()
    format_instance.execute()

    chapters: List[Dict] = load_json(format_instance.output_file)
    metadata = load_json(source.output_path)

    novel = {}
    for k, v in metadata.items():
        novel[k] = v

    novel["chapters"] = chapters

    return novel


def book_all(output_folder: Path):
    metadata_file = output_folder / "metadata.json"
    chapters_file = output_folder / "chapters.json"
    novel_file = output_folder / "novel.json"

    if not metadata_file.exists() or not chapters_file.exists():
        raise RuntimeError("Metadata or chapters file doesn't exist!")

    metadata = load_json(metadata_file)
    chapters = load_json(chapters_file)

    novel = {}
    
    for k, v in metadata.items():
        novel[k] = v
    
    novel["chapters"] = chapters

    dump_json(novel_file, novel)