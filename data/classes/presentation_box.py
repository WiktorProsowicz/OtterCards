from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.cache import Cache
from kivy.metrics import dp


class PresentationBox(Widget):

    def change_color(self, rgb_key, value):
        hex_v = hex(value).replace("0x", "")
        if len(hex_v) == 1:
            hex_v = "0" + hex_v

        if rgb_key == "red":
            self.box.color = hex_v + self.box.color[2:]

        elif rgb_key == "green":
            self.box.color = self.box.color[0:2] + hex_v + self.box.color[4:]

        else:
            self.box.color = self.box.color[:4] + hex_v

        self.refresh()

    def change_name(self, text):
        self.box.name = text
        self.refresh()

    def change_nr_compartments(self, obj=None, nr=None):
        self.box.nr_compartments = nr

    def change_special(self, special):
        self.box.is_special = special

    def refresh(self):

        if self.box is None:
            return

        font_size = self.width / 8
        self.core_l = CoreLabel(text=self.box.name, font_size=font_size,
                                text_size=(self.width - self.std_spacing * 4, None), halign="center")
        self.core_l.refresh()

        while self.core_l.texture.height > self.height / 3 - self.std_spacing * 2:
            font_size *= 0.95
            self.core_l = CoreLabel(text=self.box.name, font_size=font_size,
                                    text_size=(self.width - self.std_spacing * 4, None), halign="center")
            self.core_l.refresh()

        imgdir = Cache.get("app_info", "work_dir") + "/data/textures/"
        if self.box.nr_cards == 0:
            self.img_src = imgdir + "slider_box_empty.png"

        elif self.box.nr_cards < 50:
            self.img_src = imgdir + "slider_box_low.png"

        elif self.box.nr_cards < 100:
            self.img_src = imgdir + "slider_box_medium.png"

        else:
            self.img_src = imgdir + "slider_box_high.png"

        self.canvas.clear()
        with self.canvas:
            Color(rgba=(1, 1, 1, 1))
            Rectangle(size=(self.width * 0.9, self.width * 0.9),
                      pos=(self.x + self.width * 0.05, self.y + self.width * 0.55),
                      source=self.img_src)

            Color(rgb=get_color_from_hex("#" + self.box.color), a=.8)
            RoundedRectangle(size=(self.width * 0.65, self.width * 0.5),
                             pos=(self.x + self.width * 0.1, self.y + self.width * 0.595))

            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(self.width * 0.5, self.width * 0.5),
                      pos=(self.x + self.width * 0.2, self.y + self.height / 2.5),
                      source=Cache.get("app_info", "work_dir") + "/data/textures/otter_silhouette.png")

            Color(rgba=get_color_from_hex("#04c29c"))
            RoundedRectangle(size=(self.width, self.height / 3 - self.std_spacing),
                             pos=(self.x, self.y))

            if self.box.is_special:
                Color(rgba=get_color_from_hex("#0d614f"))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height / 3 - self.std_spacing, 10), width=2)

            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(self.core_l.texture.width, self.core_l.texture.height),
                      pos=(self.x + self.width / 2 - self.core_l.texture.width / 2,
                           self.y + self.height / 6 - self.core_l.texture.height / 2),
                      texture=self.core_l.texture)

    def __init__(self, **kwargs):
        super(PresentationBox, self).__init__(**kwargs)

        self.box = None
        self.img_src = ""
        self.core_l = CoreLabel(text="")

        self.std_spacing = dp(5)