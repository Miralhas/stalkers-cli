from ast import Dict
from pathlib import Path
from typing import List
from core.metadata import MetadataSource
from core.format import Format
from utils import load_json, dump_json


def execute(source: MetadataSource, format_instance: Format) -> Dict:
    source.extract_metadata()
    format_instance.execute()

    chapters: List[Dict] = load_json(format_instance.output_file)
    metadata = load_json(source.output_path)

    novel = {}
    for k, v in metadata.items():
        novel[k] = v

    novel["chapters"] = chapters

    return novel
