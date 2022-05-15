from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty


class ManualIncreaser(Widget):

    value = NumericProperty(0)

    def increase(self, *args):
        self.value += 1
        self.draw()

    def decrease(self, *args):
        if self.value > self.min_value:
            self.value -= 1
            self.draw()

    def draw(self, *args):
        label_text = u'∞' if self.value == -1 else str(self.value)
        self.font_size = self.height

        core_l = CoreLabel(text=label_text, font_size=self.font_size)
        core_l.refresh()

        while core_l.texture.width > self.width:
            self.font_size *= 0.95
            core_l = CoreLabel(text=label_text, font_size=self.font_size)
            core_l.refresh()

        self.canvas.clear()
        with self.canvas:
            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(core_l.texture.width, core_l.texture.height),
                      pos=(self.center_x - core_l.texture.width / 2, self.center_y - core_l.texture.height / 2),
                      texture=core_l.texture)

    def on_value(self, *args):
        self.draw()

    def __init__(self, min_value=-1, **kwargs):
        super(ManualIncreaser, self).__init__(**kwargs)

        self.font_size = None

        self.min_value = min_value
