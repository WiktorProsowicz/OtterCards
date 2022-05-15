from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.properties import BooleanProperty
from kivy.metrics import dp


class SliderChunk(Widget):

    marked = BooleanProperty(False)

    def toggle_hidden(self, *args):
        self.hidden = not self.hidden
        self.draw()

    def toggle_marked(self, *args):
        self.marked = not self.marked
        self.draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            Clock.schedule_once(self._do_hold, .15)
            touch.grab(self)
            return super(SliderChunk, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            Clock.unschedule(self._do_hold)
            return super(SliderChunk, self).on_touch_up(touch)

    def _do_hold(self, nt):
        self.dispatch("on_hold")

    def on_hold(self):
        pass

    def adjust_style(self, *args):
        width = self.parent.width - self.parent.padding[0] * 2 - self.padding * 2
        font_size = width / 22

        core_l = CoreLabel(text=self.text, font_size=font_size)
        core_l.refresh()

        if core_l.texture.width > width:
            core_l = CoreLabel(text=self.text, font_size=font_size, text_size=(width - self.padding * 2, None))
            core_l.refresh()

        self.width = core_l.texture.width + self.padding * 2
        self.height = core_l.texture.height + self.padding * 2
        self.core_l = core_l

    def draw(self, *args):
        color = "#109e82" if self.hidden else "#04c29c"
        color = "#d48f5b" if self.marked else color

        self.canvas.clear()
        with self.canvas:
            Color(rgba=get_color_from_hex(color))
            RoundedRectangle(size=self.size, pos=self.pos)
            Color(rgba=get_color_from_hex("#333333"))
            Rectangle(size=(self.core_l.texture.width, self.core_l.texture.height),
                      pos=(self.center_x - self.core_l.texture.width / 2, self.center_y - self.core_l.texture.height / 2),
                      texture=self.core_l.texture)

    def __init__(self, text: str, hidden: bool, **kwargs):
        super(SliderChunk, self).__init__(**kwargs)

        self.size_hint = (None, None)

        self.text = text
        self.hidden = hidden
        self.core_l = CoreLabel(text=self.text)
        self.core_l.refresh()

        self.padding = dp(10)

        self.register_event_type("on_hold")