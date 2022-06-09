from os.path import isfile
from data.flashcards.flashcard_database import Flashcard
from .extracting_from_dictionaries import get_entries_from_diki, get_to_english_from_babla, get_chinese_words_from_mdbg
from .flashcards.flashcards_exceptions import DictionaryError


def get_cards_from_file(filename: str, hidden_pattern: str, def_pattern: str) -> list:
    """
    basic function to handle files with def and hidden lines
    uses pattern for custom text-files styles:
        [hidden_pattern]first hidden line
        ...
        [hidden_pattern]nth hidden line
        [def_pattern]first def line
        ...
        [def pattern]nth def line
    """

    if not isfile(filename):
        return None

    flashcards = []
    mode = ""  # indicated current position of parser, tells what kind of lines is being read
    current_card = Flashcard(id=None, hidden_lines=[], def_lines=[], tags=[])

    with open(filename, encoding="utf-8") as file:
        for line in file.readlines():

            if line.startswith(hidden_pattern):
                if mode == "def":
                    flashcards.append(current_card)
                    mode = "hidden"
                    current_card = Flashcard(id=None, hidden_lines=[], def_lines=[], tags=[])  # making a new flashcard
                    pure_text = line[len(hidden_pattern):].rstrip("\n")

                    pure_text = pure_text.encode(encoding="utf-8", errors="replace")
                    while len(pure_text) >= 1000:
                        pure_text = pure_text[:-1]

                    pure_text = pure_text.decode(encoding="utf-8", errors="replace")

                    current_card.hidden_lines.append(pure_text)
                else:
                    pure_text = line[len(hidden_pattern):].rstrip("\n")
                    current_card.hidden_lines.append(pure_text)

            elif line.startswith(def_pattern):
                mode = "def"
                pure_text = line[len(def_pattern):].rstrip("\n")

                pure_text = pure_text.encode(encoding="utf-8", errors="replace")
                while len(pure_text) >= 1000:
                    pure_text = pure_text[:-1]

                pure_text = pure_text.decode(encoding="utf-8", errors="replace")

                current_card.def_lines.append(pure_text)

        flashcards.append(current_card)  # last card

    return flashcards


def get_cards_from_dictionary(filename: str, mode: str, subdefs_limit: int = None,
                              flashcards_limit: int = None, get_hinted: bool = True, **kwargs) -> tuple:
    """
    function to extract prepared words from file and search for them in dictionary with function get_entries_from_[dictionary_name]
    @:param mode indicates the dictionary_name and language e.g. polish_to_english --- polish words, diki dictionary
    this function is prepared for data in format:
        [ hidden: tuple, def: tuple, hidden: tuple ... ], extras: tuple
    @:param subdefs_limit - tells how many lines from below the label we can get
    @:param flashcards_limit - tells how many different "words" we can get
    @:param get_hinted - get additional words (only names) if possible
    """

    if filename != "":
        if not isfile(filename):
            raise FileNotFoundError

        with open(filename) as f:
            words = [line.strip("\n \t") for line in f.readlines()]
    else:
        words = kwargs.get("words", [])

    flashcards, extra_lines, exceptions = [], [], []

    for word in words:

        try:
            if mode == "english_to_polish" or mode == "polish_to_english":
                entries, extras = get_entries_from_diki(word, "english", subdefs_limit, flashcards_limit, get_hinted)

            elif mode == "german_to_polish" or mode == "polish_to_german":
                entries, extras = get_entries_from_diki(word, "german", subdefs_limit, flashcards_limit, get_hinted)

            elif mode in ("english_to_arabic", "arabic_to_english", "english_to_danish", "danish_to_english",
                          "english_to_dutch", "dutch_to_english", "english_to_finnish", "finnish_to_english",
                          "english_to_german", "german_to_english", "english_to_greek", "greek_to_english",
                          "english_to_hindi", "hindi_to_english", "english_to_norwegian", "norwegian_to_english",
                          "english_to_italian", "italian_to_english", "english_to_portuguese", "portuguese_to_english",
                          "russian_to_english", "english_to_russian", "english_to_spanish", "spanish_to_english",
                          "english_to_swedish", "swedish_to_english", "english_to_turkish", "turkish_to_english"):

                l = [l for l in mode.split("_to_") if l != "english"][0]
                entries, extras = get_to_english_from_babla(word, l, subdefs_limit, flashcards_limit, get_hinted)

            elif mode in ("chinese_to_english", "english_to_chinese"):
                entries, extras = get_chinese_words_from_mdbg(word, mode, subdefs_limit, flashcards_limit)

        except DictionaryError:
            exceptions.append(word)

        else:
            while entries:
                hidden_lines = entries.pop(0)
                def_lines = entries.pop(0)
                flashcards.append(Flashcard(id=None, def_lines=def_lines, hidden_lines=hidden_lines))

            for extra in extras:
                extra_lines.append(extra)

    return flashcards, extra_lines, exceptions
