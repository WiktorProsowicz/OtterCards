from bs4 import BeautifulSoup
from urllib import request, error
from .flashcards.flashcards_exceptions import DictionaryError

url_map = {
    "!": "%21", "#": "%23", "$": "%24", "&": "%26", "'": "%27",
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
        raise DictionaryError

    soup = BeautifulSoup(plain_html, "html.parser")

    try:
        left_column = soup.find("div", {"class": "diki-results-left-column"})
    except:
        raise DictionaryError

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
        for meaning_list in meanings:  # basically parts of speech

            meaning_lines = meaning_list.find_all("li", recursive=False)  # appropriate def lines
            for count, meaning_line in enumerate(meaning_lines):
                if subdefs_limit is not None and count == subdefs_limit:
                    break

                # omitting hidden-meanings structure
                if meaning_line.find("span", {"class": "hiddenNotForChildrenMeaning"}, recursive=False) is not None:
                    meaning_line = meaning_line.find("span", {"class": "hiddenNotForChildrenMeaning"}, recursive=False)

                line_words = meaning_line.find_all("span", {"class": "hw"}, recursive=False)
                line_str = ", ".join(word.text.strip("\t \n") for word in line_words)
                def_tuple += (line_str,)

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


def get_to_english_from_babla(word: str, language: str, subdefs_limit: int, flashcards_limit: int, get_hinted: bool,
                                   **kwargs) -> tuple:

    language_url_map = {
        "russian": "https://www.babla.ru/%D0%B0%D0%BD%D0%B3%D0%BB%D0%B8%D0%B9%D1%81%D0%BA%D0%B8%D0%B9-%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9/",
        "spanish": "https://en.bab.la/dictionary/english-spanish/",
        "turkish": "https://en.bab.la/dictionary/english-turkish/",
        "portuguese": "https://en.bab.la/dictionary/english-portuguese/",
        "greek": "https://en.bab.la/dictionary/english-greek/",
        "german": "https://en.bab.la/dictionary/english-german/",
        "hindi": "https://en.bab.la/dictionary/english-hindi/",
        "norwegian": "https://en.bab.la/dictionary/english-norwegian/",
        "italian": "https://en.bab.la/dictionary/english-italian/",
        "czech": "https://en.bab.la/dictionary/english-czech/",
        "arabic": "https://en.bab.la/dictionary/english-arabic/",
        "danish": "https://en.bab.la/dictionary/english-danish/",
        "dutch": "https://en.bab.la/dictionary/english-dutch/",
        "swedish": "https://en.bab.la/dictionary/english-swedish/",
        "finnish": "https://en.bab.la/dictionary/english-finnish/"
    }

    url = language_url_map[language] + prettify(word)

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

    try:
        plain_html = request.urlopen(request.Request(url, headers=hdr))

    except error.URLError:
        raise DictionaryError

    soup = BeautifulSoup(plain_html, "html.parser")

    content_column = soup.find("div", {"class": "content-column"})
    first_content = content_column.find_next("div", {"class": "content"})

    entries = []

    for quick_result_entry in first_content.find_all("div", {"class": "quick-result-entry"},
                                                     limit=flashcards_limit):

        left_side = quick_result_entry.find("div", {"class": "quick-result-option"})
        right_side = quick_result_entry.find("div", {"class": "quick-result-overview"})

        if left_side is None:
            break

        hidden_word_link = left_side.find("a", {"class": "babQuickResult"})

        # if first entry is the information about not finding the word, raise error
        if hidden_word_link is None:
            raise DictionaryError

        hidden_word = hidden_word_link.get_text().strip()
        def_words = []

        def_words_list = right_side.find("ul", {"class": "sense-group-results"}).find_all("li", limit=subdefs_limit)
        for list_item in def_words_list:
            list_item = list_item.find_all("a")[-1]
            def_words.append(list_item.get_text().strip())

        entries.append((hidden_word,))
        entries.append(tuple(def_words))

    if not get_hinted:
        return entries, ()

    similar_content = soup.find("div", {"id": "similarWords", "class": "content"})
    if similar_content is None:
        return entries, ()

    hinted_limit = kwargs.get("hinted_limit", 7)
    extras = []

    similar_words_list = similar_content.find("ul", {"class": "sense-group-results"})
    list_items = reversed(similar_words_list.find_all("li"))

    for item_index, list_item in enumerate(list_items):
        if list_item.get("title") is not None or item_index == hinted_limit:
            break

        extras.append(list_item.find("a").get_text().strip())

    return entries, extras


def get_chinese_words_from_mdbg(word: str, l_mode: str, subdefs_limit: int, flashcards_limit: int, get_hinted: bool) -> tuple:

    url = f"https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb={prettify(word)}"

    try:
        plain_html = request.urlopen(url)

    except error.URLError:
        raise DictionaryError

    soup = BeautifulSoup(plain_html, "html.parser")

    content_area = soup.find("div", {"id": "contentarea"})
    words_table = content_area.find("table", {"class": "wordresults"})

    if words_table is None:
        raise DictionaryError

