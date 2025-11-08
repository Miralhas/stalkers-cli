from pathlib import Path
from stalkers_cli.core import Client
from rich import print

def sync_novels(absolute_root: Path):
    client = Client()
    novels = client.get_all_novels_info()

    ar_novels = [novel_path.name for novel_path in absolute_root.iterdir() if novel_path.is_dir()]
    slugs = [novel["slug"] for novel in novels]

    for novel in novels:
        if novel["slug"] not in ar_novels:
            print(F"[red]{novel["slug"]} is stored only in the backend")
    
    for rpath in ar_novels:
        if rpath not in slugs:
            print(F"[red]{rpath} is stored only locally")


if __name__ == "__main__":
    sync_novels(Path(r'D:\Devilsect\NovelOutput'))
        
