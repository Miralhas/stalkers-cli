import nh3

OUTPUT_FOLDER_NAME="formatted-novel"

AVAILIABLE_SOURCES = ("webnoveldotcom", "novelupdates")

BLACKLIST_TEXT = [
    # "sponsored",
    "https://justread.pl/IdleNinjaEmpire.php",
    "I created a game for Android",
    "Novels.pl",
    "source of this content is",
    "New novel chapters are published on"
    "Source: ",
    "Next chapter will be updated first on this website",
    "https://",
    "novelnext",
]

BLACKLIST_SET = set(text.lower() for text in BLACKLIST_TEXT)

ALLOWED_TAGS = nh3.ALLOWED_TAGS - {'div', 'strong', 'a'}