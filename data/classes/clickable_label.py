from kivy.uix.label import Label
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.graphics import RoundedRectangle, Color
from kivy.utils import get_color_from_hex
from kivy.core.text import Label as CoreLabel


class ClickableLabel(ButtonBehavior, Label):

    # std_font = None     # initial font

    # def adjust_font(self):
    #     self.font_size = self.std_font
    #     core_l = CoreLabel(text=self.text, font_size=self.font_size)
    #     core_l.refresh()
    #     text_width = core_l.texture.width
    #
    #     while text_width > self.width:
    #         self.font_size -= 1
    #         core_l = CoreLabel(text=self.text, font_size=self.font_size)
    #         core_l.refresh()
    #         text_width = core_l.texture.width

    def toggle_mode(self, mode):

        self.canvas.before.clear()
        r = self.width / 10     # radius for rounded rectangle

        # getting width of the text to properly highlight the lettering
        core_l = CoreLabel(text=self.text, font_size=self.font_size)
        core_l.refresh()
        text_width = core_l.texture.width

        if mode == "normal":
            # self.adjust_font()
            self.canvas.before.clear()
            return None
        else:
            hex_color = "#b34724"  if mode == "deleting" else "#1b857c"
            pos_x = self.x - text_width * 0.05 if self.halign == "left" else self.center_x - text_width * 1.1 / 2
            with self.canvas.before:
                Color(rgba=get_color_from_hex(hex_color))
                RoundedRectangle(size=(text_width * 1.1, self.height), pos=(pos_x, self.y),
                                 radius=[(r, r), (r, r), (r, r), (r, r)])
            # self.font_size = self.std_font

    def on_press(self):
        if self.get_property_observers("on_release"):   # button style will be triggered only when the label is bound to some event
            self.opacity = 0.8

    def on_release(self):
        self.opacity = 1

    def __init__(self, **kwargs):
        super(ClickableLabel, self).__init__(**kwargs)