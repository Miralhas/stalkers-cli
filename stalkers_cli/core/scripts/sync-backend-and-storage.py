from pathlib import Path
from stalkers_cli.core import Client
from rich import print

if __name__ == "__main__":
    client = Client()
    novels = client.get_all_novels_info()
    rpath = Path(r"C:\Users\bob\Desktop\NovelOutput")
    rpath_novels = [novel_path.name for novel_path in rpath.iterdir() if novel_path.is_dir()]
    slugs = [novel["slug"] for novel in novels]

    for novel in novels:
        if novel["slug"] not in rpath_novels:
            print(F"[red]{novel["slug"]} is stored only in the backend")
    
    for rpath in rpath_novels:
        if rpath not in slugs:
            print(F"[red]{rpath} is stored only locally")
        
