from pathlib import Path

from stalkers_cli.utils import load_json
from rich import print


def all(root: Path):
    sources = []
    for novel in root.iterdir():
        json_dict = load_json(novel/"meta.json")
        url = json_dict.get("novel").get("url")
        if url is not None:
            name = url.split("/")[2]
            sources.append({name: url})

    print(sources)
if __name__ == "__main__":
    all(Path(r'C:\Users\bob\Desktop\NovelOutput'))