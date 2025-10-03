from enum import Enum

from .sources.abstract_source import MetadataSource
from .sources.novel_updates import NovelUpdatesSource
from .sources.royal_road import RoyalRoadSource
from .sources.webnovel_dot_com import WebnovelDotComSource


class AvailableSources(str, Enum):
    webnoveldotcom = "webnoveldotcom"
    novelupdates = "novelupdates"
    royalroad = "royalroad"


def get_source(value: AvailableSources) -> MetadataSource | None:
    match value:
        case AvailableSources.webnoveldotcom:
            return WebnovelDotComSource
        case AvailableSources.novelupdates:
            return NovelUpdatesSource
        case AvailableSources.royalroad:
            return RoyalRoadSource
