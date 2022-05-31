from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.core.text import Label as CoreLabel
from data.flashcards.flashcard_database import Tag
from kivy.metrics import dp
from kivy.uix.widget import Widget
from ..classes.utils import contrasting_color
from kivy.properties import BooleanProperty


class SliderTag(Widget):

    marked = BooleanProperty(False)

    def toggle_delete(self, *args):
        self.to_delete = not self.to_delete

        if self.to_delete:
            self.opacity = 1
            self.draw()
            with self.canvas:
                Color(rgba=get_color_from_hex("#ab0202"))
                Line(points=[(self.x, self.center_y), (self.right, self.center_y)], width=2)

        else:
            self.opacity = 0.5
            self.draw()

    def toggle_marked(self, *args):
        self.marked = not self.marked

        if self.marked:
            r = self.parent.width / 17
            with self.canvas.after:
                Color(rgba=get_color_from_hex("#b86a30"))
                Line(rounded_rectangle=(self.x, self.y, self.width, self.height, r), width=3)

        else:
            self.canvas.after.clear()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.opacity -= 0.2
            touch.grab(self)
            return super(SliderTag, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.opacity += 0.2
            self.dispatch("on_choose")
            touch.ungrab(self)
            return super(SliderTag, self).on_touch_up(touch)

    def on_choose(self):
        pass

    def draw(self, *args):
        r = self.parent.width / 13

        self.canvas.clear()
        with self.canvas:
            Color(rgba=get_color_from_hex("#" + self.tag.color))
            RoundedRectangle(size=self.size, pos=self.pos, radius=(r,))
            Color(rgba=self.color)
            Rectangle(pos=(self.center_x - self.core_l.texture.width / 2, self.center_y - self.core_l.texture.height / 2),
                      size=(self.core_l.texture.width, self.core_l.texture.height), texture=self.core_l.texture)

        if self.index == 0:
            with self.canvas:
                Line(points=[(self.parent.x, self.y - dp(5)), (self.parent.right, self.y - dp(5))])

    def adjust_style(self, *args):

        std_padding = self.parent.padding[1] * 2
        self.width = self.parent.width - std_padding

        font_size = self.width / 15

        std_padding = self.parent.padding[1] * 2

        self.core_l = CoreLabel(text=self.text, font_size=font_size)
        self.core_l.refresh()

        if self.index != 0:
            if self.core_l.texture.width > self.width - std_padding:
                self.core_l.text_size = (self.width - std_padding, None)
                # core_l.shorten, core_l.shorten_from = True, "right"
                # core_l.split_str = ""

                # my own shortening algorithm cause built-in one doesnt work
                # self.core_l.text += "..."
                # while self.core_l.texture.width > self.width - std_padding:
                #     self.core_l.text = self.core_l.text[:-4]
                #     self.core_l.text += "..."
                #     self.core_l.refresh()

            else:
                self.width = self.core_l.texture.width + std_padding

        if self.width < self.height:
            self.width = self.height

        self.core_l.halign = "center" if self.index == 0 else "left"
        self.core_l.refresh()

        self.height = self.core_l.texture.height + font_size

        self.draw()

    def __init__(self, tag: Tag, index: int,  **kwargs):
        super(SliderTag, self).__init__(**kwargs)

        self.index = index  # to ensure the difference between "all cards" tag and other - to be removed in the future

        self.tag = tag  # Tag object to carry important information
        self.text = "#" + self.tag.name if self.index != 0 else self.tag.name

        self.halign = "left" if self.index != 0 else "center"
        self.valign = "middle"
        self.size_hint = (None, None)

        self.register_event_type("on_choose")

        self.background_color = (0, 0, 0, 0)
        self.color = get_color_from_hex("#" + contrasting_color(self.tag.color))
        self.core_l = CoreLabel(text=self.text)
        self.core_l.refresh()

        self.canvas.clear()

        self.to_delete = False  # information about whether will be deleted
