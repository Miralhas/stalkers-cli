from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, Dict

import nh3
from bs4 import BeautifulSoup
from utils import ALLOWED_TAGS


class MetadataSource(ABC):
    novel_uri = ClassVar[str]
    output_path = ClassVar[Path]

    def __init__(self, novel_uri: str, output_folder: Path):
        self.novel_uri = novel_uri
        self.output_path = Path(f"{output_folder}/metadata.json")

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    def url(self) -> str:
        return self.base_url + self.novel_uri

    @abstractmethod
    def extract_metadata(self):
        pass

    def format_metadata(self, metadata_dict: Dict) -> None:
        pass

    def clean_html(self, html: str) -> str:
        """format and clean given html

        Args:
            html (str): html to be cleaned / formatted

        Returns:
            str: formatted html
        """

        html = nh3.clean(html, tags=ALLOWED_TAGS)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all():
            if "class" in tag.attrs:
                del tag["class"]

        final_html = (
            str(html).replace('"', "&quot;").replace("'", "&#39;").replace("\n", "")
        )

        return final_html

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict__})"
