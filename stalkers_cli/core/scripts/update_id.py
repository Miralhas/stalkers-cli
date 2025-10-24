from pathlib import Path

from stalkers_cli.utils import dump_json, load_json


def update(root: Path, start_value: int):
    json_dir = root / "json"
    if (not json_dir.exists()):
        raise Exception("Json Folder doesn't exists!")
    
    current_id = start_value

    for chapter_file in json_dir.glob("*.json"):
        json_dict = load_json(chapter_file)
        json_dict["id"] = current_id
        
        current_id += 1
        dump_json(chapter_file, json_dict)    

    print("Done!")


if __name__ == "__main__":
    root = Path(r'C:\Users\bob\Desktop\NovelOutput\the-calamitous-bob')
    update(root=root, start_value=57)
