from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.utils import get_color_from_hex
from .utils import contrasting_color
from kivy.graphics import Line, Rectangle, Color, Ellipse
from kivy.metrics import dp


class PresentationTag(Label):

    def change_color(self, rgb_key, value):
        hex_v = hex(value).replace("0x", "")
        if len(hex_v) == 1:
            hex_v = "0" + hex_v

        if rgb_key == "red":
            self.tag.color = hex_v + self.tag.color[2:]

        elif rgb_key == "green":
            self.tag.color = self.tag.color[0:2] + hex_v + self.tag.color[4:]

        else:
            self.tag.color = self.tag.color[:4] + hex_v

        self.color = get_color_from_hex("#" + contrasting_color(self.tag.color))
        self.refresh()

    def change_name(self, text):
        self.tag.name = text
        self.refresh()

    def refresh(self):
        # print(self.tag.color)
        core_l = CoreLabel(text="#" + self.tag.name, font_size=self.font_size)
        core_l.refresh()

        self.width = self.parent.width * 0.9  # setting the biggest allowed width
        std_padding = self.parent.width / 10

        if core_l.texture.width > self.width - std_padding:
            core_l.text += "..."
            while core_l.texture.width > self.width - std_padding:
                core_l.text = core_l.text[:-4]
                core_l.text += "..."
                core_l.refresh()
        else:
            self.width = core_l.texture.width + std_padding

        core_l.refresh()

        if self.width < self.height:
            self.width = self.height

        self.canvas.after.clear()

        with self.canvas.after:
            Color(rgba=get_color_from_hex("#" + self.tag.color))
            Rectangle(size=(self.width - self.height, self.height), pos=(self.x + self.height / 2, self.y))
            Ellipse(size=(self.height, self.height), pos=(self.x, self.y), angle_start=0, angle_end=-180)
            Ellipse(size=(self.height, self.height), pos=(self.right - self.height, self.y), angle_start=0,
                    angle_end=180)
            Color(rgba=self.color)
            Rectangle(pos=(
                self.x + self.width / 2 - core_l.texture.width / 2,
                self.y + self.height / 2 - core_l.texture.height / 2),
                size=(core_l.texture.width, core_l.texture.height), texture=core_l.texture)
            Color(rgba=get_color_from_hex("#c8c8c8"))
            Line(points=[(self.x + self.height / 2, self.y), (self.right - self.height / 2, self.y)], width=1)
            Line(points=[(self.x + self.height / 2, self.top), (self.right - self.height / 2, self.top)], width=1)
            Line(ellipse=(self.x, self.y, self.height, self.height, 0, -180), width=1)
            Line(ellipse=(self.right - self.height, self.y, self.height, self.height, 0, 180), width=1)
            Line(points=[(self.parent.x + self.parent.width * 0.1, self.y - dp(20)),
                         (self.parent.right - self.parent.width * 0.1, self.y - dp(20))], width=1)

    def __init__(self, **kwargs):
        super(PresentationTag, self).__init__(**kwargs)

        self.tag = None  # Tag object to carry important informations
        self.text = ""

        self.halign = "center"
        self.valign = "middle"

        self.background_color = (0, 0, 0, 0)
        self.color = get_color_from_hex("#222222")
