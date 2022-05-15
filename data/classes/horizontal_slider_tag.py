from kivy.uix.widget import Widget
from data.flashcards.flashcard_database import Tag
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.utils import get_color_from_hex
from .utils import contrasting_color
from kivy.clock import Clock


class HorizontalSliderTag(Widget):

    def toggle_marked(self, *args):
        self.marked = not self.marked

        if self.marked:
            self.background_color = "e68845"

        else:
            self.background_color = self.tag.color

        self.draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.grab(self)
            Clock.schedule_once(self._do_hold, .5)
            return super(HorizontalSliderTag, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            Clock.unschedule(self._do_hold)

    def _do_hold(self, nt):
        self.dispatch("on_hold")

    def adjust_style(self, *args):
        font_size = self.height * 0.5

        self.core_l = CoreLabel(text="#" + self.tag.name, font_size=font_size)
        self.core_l.refresh()

        self.width = self.core_l.texture.width + self.std_padding * 2

    def on_hold(self):
        pass

    def draw(self, *args):
        r = self.parent.height / 2  # radius

        self.canvas.clear()
        with self.canvas:
            Color(rgba=get_color_from_hex("#" + self.background_color))
            RoundedRectangle(size=self.size, pos=self.pos, radius=[(r, r), (r, r), (r, r), (r, r)])
            Color(rgba=get_color_from_hex("#" + self.color))
            Rectangle(size=(self.core_l.texture.width, self.core_l.texture.height),
                      pos=(self.center_x - self.core_l.texture.width / 2, self.y + self.height / 2 - self.core_l.texture.height / 2),
                      texture=self.core_l.texture)

    def __init__(self, tag: Tag, **kwargs):
        super(HorizontalSliderTag, self).__init__(**kwargs)

        self.tag = tag
        self.color = contrasting_color(tag.color)
        self.background_color = self.tag.color

        self.core_l = None

        self.size_hint = (None, 1)
        self.std_padding = dp(10)

        self.marked = False

        self.register_event_type("on_hold")
