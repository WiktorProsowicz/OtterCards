from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from data.flashcards.flashcard_database import Box
from kivy.cache import Cache
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.utils import get_color_from_hex


class SliderBox(Widget):

    def toggle_delete(self, *args):
        self.to_delete = not self.to_delete

        if self.to_delete:
            self.opacity = 1.0
            with self.canvas.before:
                Color(rgb=get_color_from_hex("#ab0202"), a=.7)
                RoundedRectangle(pos=self.pos, size=self.size)
        else:
            self.opacity = 0.5
            self.canvas.before.clear()

    def adjust_style(self, *args):
        self.height = self.width * 1.5

        imgdir = Cache.get("app_info", "work_dir") + "/data/textures/"

        if self.box.nr_cards == 0:
            self.img_src = imgdir + "slider_box_empty.png"

        elif self.box.nr_cards < 50:
            self.img_src = imgdir + "slider_box_low.png"

        elif self.box.nr_cards < 100:
            self.img_src = imgdir + "slider_box_medium.png"

        else:
            self.img_src = imgdir + "slider_box_high.png"

        font_size = self.width / 8
        self.core_l = CoreLabel(text=self.box.name, font_size=font_size,
                                text_size=(self.width - self.std_spacing * 4, None), halign="center")
        self.core_l.refresh()

        while self.core_l.texture.height > self.height / 3 - self.std_spacing * 2:
            font_size *= 0.95
            self.core_l = CoreLabel(text=self.box.name, font_size=font_size,
                                    text_size=(self.width - self.std_spacing * 4, None), halign="center")
            self.core_l.refresh()

    def draw(self, *args):

        self.canvas.clear()
        with self.canvas:
            # Color(rgba=get_color_from_hex("#666666"))
            # Rectangle(size=self.size, pos=self.pos)

            Color(rgba=(1, 1, 1, 1))
            Rectangle(size=(self.width * 0.9, self.width * 0.9), pos=(self.x + self.width * 0.05, self.y + self.width * 0.55),
                      source=self.img_src)

            Color(rgb=get_color_from_hex("#" + self.box.color), a=.8)
            RoundedRectangle(size=(self.width * 0.65, self.width * 0.5),
                      pos=(self.x + self.width * 0.1, self.y + self.width * 0.595))

            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(self.width * 0.5, self.width * 0.5), pos=(self.x + self.width * 0.2, self.y + self.height / 2.5),
                      source=Cache.get("app_info", "work_dir") + "/data/textures/otter_silhouette.png")

            Color(rgba=get_color_from_hex("#04c29c"))
            RoundedRectangle(size=(self.width, self.height / 3 - self.std_spacing),
                             pos=(self.x, self.y))

            if self.box.is_special:
                Color(rgba=get_color_from_hex("#0d614f"))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height / 3 - self.std_spacing, 10), width=2)

            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(self.core_l.texture.width, self.core_l.texture.height),
                      pos=(self.x + self.width / 2 - self.core_l.texture.width / 2, self.y + self.height / 6 - self.core_l.texture.height / 2),
                      texture=self.core_l.texture)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.grab(self)
            self.opacity -= 0.2
            return super(SliderBox, self).on_touch_down(touch)

    def on_choose(self):
        pass

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.dispatch("on_choose")
            self.opacity += 0.2
            touch.ungrab(self)
            return super(SliderBox, self).on_touch_up(touch)

    def __init__(self, box: Box, **kwargs):
        super(SliderBox, self).__init__(**kwargs)

        self.size_hint = (0.45, None)

        self.box = box      # Box object to carry info

        self.core_l = CoreLabel(text="")
        self.core_l.refresh()
        self.img_src = None

        self.std_spacing = dp(5)

        self.register_event_type("on_choose")

        self.to_delete = False
