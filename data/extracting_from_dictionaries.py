from bs4 import BeautifulSoup
from urllib import request, error

url_map= {
    "!": "%21", "#": "%23", "$": "%24", "&": "%26",  "'": "%27",
    "(": "%27", ")": "%27", "*": "%27", "+": "%27", ",": "%27",
    "/": "%27", ":": "%27", ";": "%27", "=": "%27", "?": "%27",
    "@": "%27", "[": "%27", "]": "%27", " ": "%20"
}

url_safe_chars = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O",
    "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d",
    "e", "f", "g", "h", "i", "j", "k", "m", "n", "o", "p", "q", "r", "s", "t",
    "u", "v", "w", "x", "y", "z", "-", "_", ".", "~"
]


def prettify(word: str):
    new_str = ""
    for char in word:
        if char in url_map.keys():
            new_str += url_map[char]

        elif char in url_safe_chars:
            new_str += char

        else:
            char = char.encode(encoding="utf-8")
            new_str += str(char)[2:-1].replace("\\x", "%")

    return new_str


def get_entries_from_diki(word: str, language: str, subdefs_limit: int, flashcards_limit: int,
                          get_hinted: bool, **kwargs) -> tuple:
    """
    function to extract all entries from diki dictionary
    handles both english to polish, polish to english
    """
    if language == "english":
        url = f"https://www.diki.pl/slownik-angielskiego?q={prettify(word)}"
    elif language == "german":
        url = f"https://www.diki.pl/slownik-niemieckiego?q={prettify(word)}"

    try:
        plain_html = request.urlopen(url).read()
    except error.URLError:
        return None, None

    soup = BeautifulSoup(plain_html, "html.parser")

    try:
        left_column = soup.find("div", {"class": "diki-results-left-column"})
    except:
        return None, None

    entries = []

    entities = left_column.find_all("div", {"class": "dictionaryEntity"})
    for entity_count, entity in enumerate(entities):
        if flashcards_limit is not None and entity_count == flashcards_limit:
            break

        hidden_tuple = ()
        headings = entity.find("div", {"class": "hws"}).find_all("span", {"class": "hw"})

        for heading in headings:
            hidden_tuple += (heading.text.strip("\t \n"),)

        # find meanings list with both modes
        meanings = entity.findAll("ol", {"class": "foreignToNativeMeanings"})
        if not meanings:
            meanings = entity.find_all("ol", {"class": "nativeToForeignEntrySlices"})
        if not meanings:
            continue

        def_tuple = ()
        for meaning_list in meanings:   # basically parts of speech

            meaning_lines = meaning_list.find_all("li", recursive=False)  # appropriate def lines
            for count, meaning_line in enumerate(meaning_lines):
                if subdefs_limit is not None and count == subdefs_limit:
                    break

                # omitting hidden-meanings structure
                if meaning_line.find("span", {"class": "hiddenNotForChildrenMeaning"}, recursive=False) is not None:
                    meaning_line = meaning_line.find("span", {"class": "hiddenNotForChildrenMeaning"}, recursive=False)

                line_words = meaning_line.find_all("span", {"class": "hw"}, recursive=False)
                line_str = ", ".join(word.text.strip("\t \n") for word in line_words)
                def_tuple += (line_str, )

        entries.append(hidden_tuple)
        entries.append(def_tuple)

    if not get_hinted:
        return entries, ()

    right_column = soup.find("div", {"class": "diki-results-right-column"})
    if right_column is None:
        return entries, ()

    extras_limit = kwargs.get("hinted_limit", 10)
    extras = ()

    # slingle lines from right column regardless of the speech part
    fentries = right_column.find_all("div", {"class": "fentry"})
    for count, fentry in enumerate(fentries):
        if count == extras_limit:
            break

        fentrymain = fentry.find("span", {"class": "fentrymain"})
        word = fentrymain.find("span", {"class": "hw"}).text.strip("\n \t")

        extras += (word,)

    return entries, extras
