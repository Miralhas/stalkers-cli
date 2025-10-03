from pathlib import Path
import math
import subprocess

default_options = {
    "filename_only": "--filename_only",
    "single": "--single",
    "suppress": "--suppress",
    "format": "--format json",
    "close_directly": "--close-directly",
    "add_source_url": "--add-source-url",
    "ignore_images": "--ignore-images",
}


def create_ps1(scripts: list[str], output: Path, sleep: int) -> str:
    ps1_file = f"{Path(f"{output}/scripts.ps1")}"
    
    with open(output / "scripts.ps1", "w") as file:
        file.write(f"# powershell.exe -noexit -file {ps1_file}\n")
        file.write("Set-Location -Path C:\\Users\\bob\\Desktop\\lightnovel-crawler\n")
        file.write(".\\.venv\\Scripts\\activate\n")

        for script in scripts:
            file.write(f"{script}\nStart-Sleep -Seconds {sleep}\n")

    return ps1_file


def build_script(source: str, output: Path, range: tuple[int, int]):
    script = (
        f'py .\\lncrawl\\ -s "{source}" -i -o "{output}" --range {range[0]} {range[1]} '
    )

    for option in default_options.values():
        script += f"{option} "

    return script


def generate_download_list(end_index: int, range_chapters: int, start_index: int, source: str, output: Path, sleep: int) -> str:
    scripts = []
    total = math.ceil((end_index - start_index) / range_chapters)
    start = start_index
    last = start + range_chapters - 1

    for _ in range(total):
        script = build_script(
            source=source,
            output=output,
            range=(start, last),
        )
        scripts.append(script)

        start = last
        new_last = start + range_chapters
        last = new_last if new_last < end_index else end_index

    return create_ps1(scripts, output, sleep)


def execute_ps1_script(ps1_file: Path):
    subprocess.Popen([
        "powershell.exe",
        "-Command",
        f"Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"{ps1_file}\"'"
    ])


if __name__ == "__main__":
    end_index = 858
    start_index = 750
    range_chapters = 20
    path = Path(r"C:\Users\bob\Desktop\NovelOutput\the-authors-pov")
    path.mkdir(parents=True, exist_ok=True)

    scripts = generate_download_list(
        end_index=end_index,
        range_chapters=range_chapters,
        start_index=start_index,
        source="https://novelnext.com/books/the-authors-pov",
        output=path,
        sleep=5
    )
