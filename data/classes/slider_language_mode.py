from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex


class SliderLanguageMode(Widget):

    def on_choose(self):
        pass
    
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.grab(self)
        return super(SliderLanguageMode, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.dispatch("on_choose")
            touch.ungrab(self)
        return super(SliderLanguageMode, self).on_touch_down(touch)

    def draw(self, *args):
        self.height = self.width / 2
        self.font_size = self.height / 4

        if self.language_mode is not None:
            lang1, lang2 = self.language_mode.split("_")[0], self.language_mode.split("_")[2]
            label_text = u"%s ↦ %s" % (lang1, lang2)
        else:
            label_text = "no language mode"

        core_l = CoreLabel(text=label_text, font_size=self.font_size)
        core_l.refresh()

        while core_l.texture.width > self.width:
            self.font_size *= 0.95
            core_l = CoreLabel(text=label_text, font_size=self.font_size)
            core_l.refresh()

        self.canvas.clear()
        with self.canvas:
            Color(rgba=(1, 1, 1, 1))
            Rectangle(size=(self.height * 1.5, self.height * 0.75),
                      pos=(self.center_x - self.height * 0.75, self.y + self.height * 0.25),
                      source=f"atlas://data/textures/atlas/language_modes/{self.language_mode}")
            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(core_l.texture.width, core_l.texture.height),
                      pos=(self.center_x - core_l.texture.width / 2, self.y),
                      texture=core_l.texture)

    def __init__(self, language_mode: str = None, **kwargs):
        super(SliderLanguageMode, self).__init__(**kwargs)

        self.language_mode = language_mode
        self.font_size = None

        self.register_event_type("on_choose")
