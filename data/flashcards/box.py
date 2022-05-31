class Box:

    def __str__(self):
        return "ID: {}\nNAME: {}\nNR_CARDS: {}\nNR_COMPS: {}\nCOLOR: {}\nLAST_UPDATE: {}" \
               "\nCREATION_DATE:{}\nIS_SPECIAL:{}".format(
                self.id, self.name, self.nr_cards, self.nr_compartments, self.color, self.last_update,
                self.creation_date, self.is_special)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)

        self.nr_cards = kwargs.get("nr_cards", 0)
        self.nr_compartments = kwargs.get("nr_compartments", 0)
        self.color = kwargs.get("color", "000000")
        self.name = kwargs.get("name", "")
        self.last_update = kwargs.get("last_update", 0)
        self.creation_date = kwargs.get("creation_date", 0)
        self.is_special = kwargs.get("is_special", False)
        self.cards_left = kwargs.get("cards_left", 0)

        self.is_redundant = kwargs.get("is_redundant", False)