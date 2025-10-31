from pathlib import Path
from stalkers_cli.core import Client
from rich import print

if __name__ == "__main__":
    client = Client()
    novels = client.get_all_novels_info()
    rpath = Path(r"C:\Users\bob\Desktop\NovelOutput")
    rpath_novels = [novel_path.name for novel_path in rpath.iterdir() if novel_path.is_dir()]

    for novel in novels:
        if novel["slug"] not in rpath_novels:
            print(F"[red]{novel["slug"]} is FUCKING MISMATCHED !!!!!!!!!!!!")
        
