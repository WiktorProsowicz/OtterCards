from kivy.uix.bubble import Bubble, BubbleButton
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle
from kivy.utils import get_color_from_hex


class DismissableBubble(Bubble):

    def dismiss(self, *args):
        hide_anim = Animation(opacity=0, duration=.1)
        hide_anim.bind(on_complete=lambda anim, time: self.root_layout.clear_widgets())
        hide_anim.start(self)

    def show(self, *args):
        self.opacity = 0
        self.root_layout.add_widget(self)
        show_anim = Animation(opacity=1, duration=.3)
        show_anim.start(self)

    def __init__(self, layout, **kwargs):
        super(DismissableBubble, self).__init__(**kwargs)
        self.root_layout = layout


class DismissableBubbleButton(BubbleButton):

    def draw(self, *args):
        width = min(self.width, self.height) * 0.9

        self.canvas.clear()
        with self.canvas:
            Color(rgba=get_color_from_hex("#0d856f"))
            if self.shape == "round":
                Ellipse(pos=(self.center_x - width / 2, self.center_y - width / 2),
                        size=(width, width), angle_start=0, angle_end=360)
            elif self.shape == "square":
                RoundedRectangle(pos=(self.center_x - self.width * 0.9 / 2, self.center_y - self.height * 0.9 / 2),
                                 size=(self.width * 0.9, self.height * 0.9))

            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(pos=(self.center_x - width * 0.7 / 2, self.center_y - width * 0.7 / 2),
                      size=(width * 0.7, width * 0.7), source=self.icon_src)

    def on_release(self):
        self.opacity += 0.2

    def on_press(self):
        self.opacity -= 0.2

    def __init__(self, icon_src, shape="round", **kwargs):
        super(DismissableBubbleButton, self).__init__(**kwargs)

        self.icon_src = icon_src

        self.bind(pos=self.draw, size=self.draw)
        self.always_release = True

        self.shape = shape