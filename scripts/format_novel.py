import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List

import nh3
from bs4 import BeautifulSoup
from slugify import slugify

logging.basicConfig(level=logging.INFO)

ALLOWED_TAGS = nh3.ALLOWED_TAGS - {'div', 'strong'}

# text to remove if it is present in the html
BLACKLIST_TEXT = [
    "ads",
    "sponsored",
    "https://justread.pl/IdleNinjaEmpire.php",
    "I created a game for Android",
    "Novels.pl",
    "source of this content is",
    "New novel chapters are published on",
]

# only tags allowed in the html
HTML_TAGS_SAFELIST = [
    "a",
    "b",
    "blockquote",
    "br",
    "cite",
    "code",
    "dd",
    "dl",
    "dt",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "q",
    "small",
    "span",
    "strike",
    "strong",
    "sub",
    "sup",
    "u",
    "ul",
    "div"
]

BLACKLIST_SET = set(text.lower() for text in BLACKLIST_TEXT)

def load_json(file_path: Path) -> Dict:
    """Load JSON data from a file."""
    try:
        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON from {file_path}: {e}") from e


def save_json(data: Dict, output_path: Path) -> None:
    """Safely save a dictionary to a JSON file."""
    try:
        with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', dir=output_path.parent) as tmp_file:
            json.dump(data, tmp_file, indent=4, ensure_ascii=False)
            tmp_path = Path(tmp_file.name)
        tmp_path.replace(output_path)
        logging.info(f"Saved JSON to: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to save JSON to {output_path}: {e}") from e


def extract_nested_keys(source: Dict, section: str) -> Dict:
    """
    Extract specific keys from a nested section of a dictionary.

    Args:
        source (Dict): The entire JSON dictionary.
        section (str): Top-level key where data is nested (e.g., 'novel').
    Returns:
        Dict: Dictionary with only the selected keys.
    """
    nested_data = source.get(section, {})
    keys_dict = {}
    for key in nested_data.keys():
        if key == "chapters":
            # remove every chapter file that failed (was not downloaded)
            nested_data["chapters"][:] = [chapter for chapter in nested_data["chapters"] if chapter["success"] != False]
        keys_dict.update({key: nested_data[key]})

    # return {key: nested_data[key] for key in nested_data.keys()}
    return keys_dict


def format_chapters(
    extracted: Dict[str, List[Dict]], keys: List[str] = ["id", "title", "body"]
) -> None:
    """Reduce chapter data to only specified keys."""
    if "chapters" in extracted:
        extracted["chapters"] = [
            {"number": chapter.get("id"), **{k: chapter.get(k) for k in keys}}
            for chapter in extracted["chapters"]
        ]


def update_chapter_body(extracted: Dict, chapter_data: Dict) -> None:
    """Update the body of a chapter in the extracted data."""
    chap_id = chapter_data.get("id")
    if chap_id is not None:
        
        chapters_by_id = {chapter["id"]: chapter for chapter in extracted.get("chapters", [])}
        
        if chap_id in chapters_by_id:
            chapters_by_id[chap_id]["body"] = clean_chapter_body(
                chapter_data.get("body"), chapter_data.get("title")
            )
        else:
            logging.warning(f"ID {chap_id} not found in extracted data")
    else:
        logging.warning("Chapter ID is missing")


def clean_chapter_body(html: str, chapter_title: str) -> str:
    """Sanitize and remove unwanted tags from the provided html."""
    
    tags = ALLOWED_TAGS
    clean_html = nh3.clean(html, tags=tags)

    soup = BeautifulSoup(clean_html, "html.parser")

 
    for tag in soup.find_all():
        if tag.name == "p":
            p_text = tag.get_text(strip=True).lower()
            if any(bad_text in p_text for bad_text in BLACKLIST_SET):
                tag.decompose()

            # Some novels have the chapter title in a <p> tag. If so, then remove it.
            if p_text == chapter_title.lower().strip():
                tag.decompose()
    
    # remove chapter title that is not in a header tag
    for element in soup.find_all(string=True):
        if (element.strip().lower() == chapter_title.strip().lower() and element.parent.name not in {"h1", "h2", "h3", "p"}):
            element.extract()

    final_html = str(soup)

    final_html = final_html.replace('"', '&quot;').replace("'", '&#39;')

    return final_html


def embed_full_chapter_data(
    extracted_path: Path, chapter_files_folder: Path, output_path: Path
) -> None:
    """Embed full chapter data by reading the body of each chapter and adding it."""

    extracted = load_json(extracted_path)

    # Iterate over all JSON chapter files in the folder
    for chapter_file in chapter_files_folder.glob("*.json"):
        try:
            chapter_data = load_json(chapter_file)
            update_chapter_body(extracted, chapter_data)
        except RuntimeError as e:
            logging.error(f"Failed to process {chapter_file}: {e}")

    save_json(extracted, output_path)
    logging.info(f"Full chapter data embedded and saved to: {output_path}")


def execute(root: str):
    input_file = Path(f"{root}/meta.json")
    chapter_files_folder = Path(f"{root}/json")

    data = load_json(input_file)
    extracted = extract_nested_keys(data, "novel")

    format_chapters(extracted)

    output_folder = Path(f"{root}/formatted-novel")
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = Path(f"{output_folder}/novel.json")

    save_json(extracted, output_file)

    embed_full_chapter_data(
        extracted_path=output_file,
        chapter_files_folder=chapter_files_folder,
        output_path=output_file,
    )

if __name__ == "__main__":
    execute("C:/Users/bob/Desktop/NovelOutput/OutsideOfTime/800")

