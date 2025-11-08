from pathlib import Path
from bs4 import BeautifulSoup

def parse_html(html_path: Path):
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()


def do(soup: BeautifulSoup):
    stops = soup.find_all("div", class_=["mbp_pagebreak"])
    chapter_count = 0

    for stop in stops:
        if stop.find_parent("div", class_="block"):
            continue

        chapter_count += 1

        wrapper = soup.new_tag("div", attrs={
            "class": "block",
            "id": f"chapter-{chapter_count}"
        })

        # stop.insert_before(wrapper)

        # wrapper.append(stop.extract())

        print(chapter_count)

        current = wrapper
        next_tag = current.find_next_sibling()

        while next_tag and next_tag.name != "div":
            to_move = next_tag
            next_tag = to_move.find_next_sibling()
            wrapper.append(to_move.extract())
    

def write(soup: BeautifulSoup, output: Path):
    with open(output, "w", encoding="utf-8") as html_file:
        html_file.write(str(soup))


if __name__ == "__main__":
    input = Path(r"C:\Users\bob\Desktop\twig\book.html")
    output = Path(r"C:\Users\bob\Desktop\twig\book-f.html")
    soup = BeautifulSoup(parse_html(input), "html.parser")

    do(soup)
    write(soup, output)