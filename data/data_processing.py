from os.path import isfile
from data.flashcards.flashcard_database import Flashcard
from .extracting_from_dictionaries import get_entries_from_diki


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
    mode = ""    # indicated current position of parser, tells what kind of lines is being read
    current_card = Flashcard(id=None, hidden_lines=[], def_lines=[], tags=[])

    with open(filename, encoding="utf-8") as file:
        for line in file.readlines():

            if line.startswith(hidden_pattern):
                if mode == "def":
                    flashcards.append(current_card)
                    mode = "hidden"
                    current_card = Flashcard(id=None, hidden_lines=[], def_lines=[], tags=[])   # making a new flashcard
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

        flashcards.append(current_card)     # last card

    return flashcards


def get_cards_from_dictionary(filename: str, mode: str, subdefs_limit: int = None,
                              flashcards_limit: int = None, get_hinted: bool = True, **kwargs) -> tuple:
    """
    function to extract prepared words from file and search for them in dictionary with function get_entries_from_[dictionary_name]
    mode indicates the dictionary_name and language e.g. polish_to_english --- polish words, diki dictionary
    this function is prepared for data in format:
        [ hidden: tuple, def: tuple, hidden: tuple ... ], extras: tuple
    subdefs_limit - tells how many lines from below the label we can get
    flashcards_limit - tells how many different "words" we can get
    get_hinted - get additional words (only names) if possible
    """
    if filename != "":
        if not isfile(filename):
            return None, None, None

        with open(filename) as f:
            words = [line.strip("\n \t") for line in f.readlines()]
    else:
        words = kwargs.get("words", [])

    flashcards, extra_lines, exceptions = [], [], []

    for word in words:
        if mode == "english_to_polish" or mode == "polish_to_english":
            entires, extras = get_entries_from_diki(word, "english", subdefs_limit, flashcards_limit, get_hinted)

        elif mode == "german_to_polish" or mode == "polish_to_german":
            entires, extras = get_entries_from_diki(word, "german", subdefs_limit, flashcards_limit, get_hinted)

        else:
            return None, None, None

        if entires is not None:
            while entires:
                hidden_lines = entires.pop(0)
                def_lines = entires.pop(0)
                flashcards.append(Flashcard(id=None, def_lines=def_lines, hidden_lines=hidden_lines))

            for extra in extras:
                extra_lines.append(extra)

        else:
            exceptions.append(word)

    return flashcards, extra_lines, exceptions