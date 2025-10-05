import json
import logging
import os
from pathlib import Path
from time import time
from typing import Dict

from rich import print

logging.basicConfig(level=logging.INFO)

def load_json(file_path: Path) -> Dict:
    """Load JSON data from a file."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            # logging.info("Loading JSON file into a dictionary...")
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON from {file_path}: {e}")


def dump_json(output_path: Path, data: Dict) -> None:
    """Dump data into a JSON file"""
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            logging.info("Dumping data into a JSON file...")
            json.dump(data, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise RuntimeError(f"Failed to dump JSON file on {output_path}: {e}")


# Timer decorator
def timer(name:str):
    def decorator(func):
        def wrap_func(*args, **kwargs):
            t1 = time()
            result = func(*args, **kwargs)
            t2 = time()
            print(f'[italic blue]{name} took {(t2-t1):.4f}s[/italic blue]')
            return result
        return wrap_func
    return decorator

import typer


def open_in_file_explorer(output_path: Path):
    """
    Propmt asking if the user wants to open the output path in the file explorer.
    """
    open_output = typer.confirm("Open output folder?", default=True)
    if (open_output):
        os.startfile(output_path)