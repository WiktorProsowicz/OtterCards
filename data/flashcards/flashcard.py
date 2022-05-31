class Flashcard:

    def __str__(self):
        return "ID: {}\nTAGS: {}\nLAST_UPDATE: {}\nHIDDEN:\n{}\nDEF:\n{}".format(
            self.id,  self.tags, self.last_update, self.hidden_lines, self.def_lines
        )

    # method used not to compare whole card but only id
    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False

    def __copy__(self):
        card = Flashcard(id=self.id, creation_date=self.last_update,
                         def_lines=None, hidden_lines=None)
        card.hidden_lines = self.hidden_lines.copy()
        card.def_lines = self.def_lines.copy()
        card.tags = self.tags.copy()
        return card

    def __init__(self, **kwargs):

        self.id = kwargs.get("id", None)

        lines = kwargs.get("def_lines", [])
        if type(lines) is list:
            self.def_lines = lines
        elif type(lines) is tuple:
            self.def_lines = list(lines)
        elif type(lines) is str:
            self.def_lines = []
            for line in lines.split("\n"):
                self.def_lines.append(line.strip())

        lines = kwargs.get("hidden_lines", [])
        if type(lines) is list:
            self.hidden_lines = lines
        elif type(lines) is tuple:
            self.hidden_lines = list(lines)
        elif type(lines) is str:
            self.hidden_lines = []
            for line in lines.split("\n"):
                self.hidden_lines.append(line.strip())

        self.tags = []
        if "tags" in kwargs.keys():
            if type(kwargs["tags"]) is list:
                for tag in kwargs["tags"]:
                    if tag not in self.tags:
                        self.tags.append(tag)
            elif type(kwargs["tags"]) is str:
                for tag in kwargs["tags"].split(";"):
                    if tag not in self.tags:
                        self.tags.append(tag)

        self.is_redundant = kwargs.get("is_redundant", False)
        self.last_update = kwargs.get("last_update", 0)

        self.comp_nr = kwargs.get("comp_nr", None)
