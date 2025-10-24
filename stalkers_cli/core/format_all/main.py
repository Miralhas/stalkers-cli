from ast import Dict
from typing import List

from stalkers_cli.core.format import Format
from stalkers_cli.core.metadata import MetadataSource
from stalkers_cli.utils import load_json


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
