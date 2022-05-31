from kivy.uix.button import Button
from kivy.graphics import Line, Color, Ellipse, Rectangle
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.metrics import dp


class UtensilButton(Button):

    def change_mode(self, mode: str):
        if mode == "enabled":
            self.icon_src = self.enabled_src
            self.opacity = 1
        elif mode == "chosen":
            self.icon_src = self.chosen_src
            self.opacity = 1
        elif mode == "disabled":
            self.opacity = 0.5

        self.draw()

    def on_press(self):
        self.bg_color = "#7beadd"
        self.draw()

    def on_release(self):
        self.bg_color = "#1fc1ab"
        self.draw()

    def draw(self, *args):

        self.texture = Image(source=self.icon_src, size=self.size).texture

        self.canvas.after.clear()
        with self.canvas.after:
            Color(rgba=get_color_from_hex(self.bg_color))
            Ellipse(pos=self.pos, size=self.size, angle_start=0, angle_end=360)
            Rectangle(
                pos=(self.x + self.width / 2 - self.width / 1.7 / 2, self.y + self.height / 2 - self.height / 1.7 / 2),
                size=(self.width / 1.7, self.height / 1.7), texture=self.texture)
            Color(rgba=get_color_from_hex("#1da89f"))
            Line(ellipse=(self.x, self.y, self.width, self.width, 0, 360), width=2)

    def __init__(self, enabled_src="", chosen_src="", **kwargs):
        super(UtensilButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.size_hint = (None, None)
        self.always_release = True

        self.enabled_src = enabled_src
        self.chosen_src = chosen_src

        self.icon_src = self.enabled_src
        self.mode = "enabled"

        self.inner_opacity = 1

        self.bg_color = "#1fc1ab"


class UtensilDropUp(BoxLayout):

    def toggle_active(self):
        self.active = not self.active

    def toggle(self, obj, direction="up", **kwargs):  # obj is a more_btn and is used to proper positioning of the dropup
        mode = kwargs.get("mode", None)

        # reassuring that dropup won't be toggled open/close "again"
        if mode == "open" and self.open:
            return None
        elif mode == "close" and not self.open:
            return None

        if self.active:
            self.open = not self.open
            if not self.open:
                self.active = False
                wipe_out = Animation(duration=.3, opacity=0)
                wipe_out.start(self)
                wipe_out.bind(on_complete=lambda anim, obj: self.clear_widgets())
                wipe_out.bind(on_complete=lambda anim, obj: self.toggle_active())

            else:
                self.active = False

                self.height, cumulative_space = 0, 0

                for key, item in self.items.items():
                    self.add_widget(item)
                    cumulative_space += item.height + self.spacing

                self.size = (obj.width, cumulative_space)
                self.pos = (obj.x, obj.top + self.spacing) if direction == "up" else (obj.x, obj.y - self.height)

                wipe_in = Animation(duration=.3, opacity=1)
                wipe_in.start(self)
                wipe_in.bind(on_complete=lambda anim, obj: self.toggle_active())

    def __init__(self, **kwargs):
        super(UtensilDropUp, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(20)

        self.open = False
        self.active = True
        self.items = {}
