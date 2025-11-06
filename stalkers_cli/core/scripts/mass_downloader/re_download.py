
from pathlib import Path
import subprocess

from stalkers_cli.utils import load_json
from rich import print
import questionary
from questionary import Choice

slugs = [
    "beast-world-i-became-the-little-villains-mommy",
    "black-quantiarch-the-progenitors-odyssey",
    "carlottas-daily-report",
    "cultivating-with-top-enlightenment",
    "harem-startup-the-demon-billionaire-is-on-vacation",
    "hero-or-villain-both",
    "high-martial-arts-invincible-starts-from-basic-archery",
    "imagination-system-i-can-build-anything",
    "my-dragon-king-system",
    "my-food-stall-serves-sss-grade-delicacies",
    "reawakening-primordial-dragon-with-limitless-mana",
    "reborn-as-the-failed-lord-with-my-resource-gathering-system",
    "reincarnated-as-a-wonderkid",
    "reincarnated-with-a-lucky-draw-system",
    "the-mute-wife-who-brings-prosperity",
    "zombie-apocalypse-i-have-safe-zone-superpower",
]

def get_source(novel_path: Path):
    novel_dict = load_json(novel_path/"meta.json")
    return novel_dict.get("novel").get("url")


def execute_lncrawl(source: str, output_path: Path):
    base_dir = Path(r"C:\Users\bob\desktop\lightnovel-crawler")
    venv_python = base_dir / ".venv" / "Scripts" / "python.exe"
    lncrawl_script = base_dir / "lncrawl"

    cmd = [
        str(venv_python),
        str(lncrawl_script),
        "-s",
        source,
        "-o",
        str(output_path),
        "--filename_only",
        "--single",
        "--suppress",
        "--format",
        "json",
        "--close-directly",
        "--add-source-url",
        "--ignore-images",
        "--all",
    ]

    subprocess.run(cmd)

def re_download_by_root(root_path: Path):
    for novel in list(root_path.iterdir()):
        if novel.is_dir():
            src = get_source(novel)
            if src is not None:
                print(f"\n[green]{novel.name}[/green]")
                execute_lncrawl(src, novel)


def re_download_all(novels: list[Path]):
    novels_to_re_download = questionary.checkbox(
        f"\n\nNovels to be re-downloaded [{len(novels)}]",
        choices=[Choice(title=novel.name, value=novel, checked=True) for novel in novels],
    ).ask()

    for index, novel in enumerate(novels_to_re_download):
        src = get_source(novel)
        if src is not None:
            print(f"\n[bright_white][{index+1}/{len(novels_to_re_download)}] Re-downloading[/bright_white][green] {novel.name}[/green]")
            execute_lncrawl(src, novel)


if __name__ == "__main__":
    root = Path(r'C:\Users\bob\Desktop\mass_download\webnoveldotcom\bi-annual')
    re_download_by_root(root)