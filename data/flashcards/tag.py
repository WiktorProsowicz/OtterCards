class Tag:

    def __str__(self):
        return "ID: {}, NAME: {}, COLOR: {}, LAST_UPDATE: {}".format(self.id, self.name, self.color, self.last_update)

    def __init__(self, tag_id = None, name: str = "", color: str = "000000", last_update: int = 0):
        self.id = tag_id
        self.name = name
        self.color = color
        self.last_update = last_update
