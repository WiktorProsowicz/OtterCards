from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, BorderImage
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import DragBehavior
from kivy.metrics import dp
from .utils import point_dist, num_in_range


class CroppingRectangle(DragBehavior, Widget):

    def on_touch_down(self, touch):
        tr = self.touch_range
        touch_pt = (touch.x, touch.y)

        if point_dist(touch_pt, (self.x, self.top)) <= tr:
            self.resize_part = "left-up"
            self.resizable = True

        elif point_dist(touch_pt, (self.right, self.top)) <= tr:
            self.resize_part = "right-up"
            self.resizable = True

        elif point_dist(touch_pt, (self.right, self.y)) <= tr:
            self.resize_part = "right-bottom"
            self.resizable = True

        elif point_dist(touch_pt, (self.x, self.y)) <= tr:
            self.resize_part = "left_bottom"
            self.resizable = True

        elif num_in_range(touch.x, (self.x, self.right)) and num_in_range(touch.y, (self.top - tr, self.top + tr)):
            self.resize_part = "up"
            self.resizable = True

        elif num_in_range(touch.x, (self.x, self.right)) and num_in_range(touch.y, (self.y - tr, self.y + tr)):
            self.resize_part = "bottom"
            self.resizable = True

        elif num_in_range(touch.y, (self.y, self.top)) and num_in_range(touch.x, (self.x - tr, self.x + tr)):
            self.resize_part = "left"
            self.resizable = True

        elif num_in_range(touch.y, (self.y, self.top)) and num_in_range(touch.x, (self.right - tr, self.right + tr)):
            self.resize_part = "right"
            self.resizable = True

        else:
            return super(CroppingRectangle, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        self.resizable = False
        return super(CroppingRectangle, self).on_touch_up(touch)

    def on_touch_move(self, touch):
        old_width = self.width
        old_height = self.height
        old_x = self.x
        old_y = self.y

        if self.resizable:
            if self.resize_part == "left-up":
                self.width = self.right - touch.x
                self.height = touch.y - self.y
                self.x = touch.x

            elif self.resize_part == "right-bottom":
                self.width = touch.x - self.x
                self.height = self.top - touch.y
                self.y = touch.y

            elif self.resize_part == "left_bottom":
                self.width = self.right - touch.x
                self.height = self.top - touch.y
                self.x = touch.x
                self.y = touch.y

            elif self.resize_part == "right-up":
                self.width = touch.x - self.x
                self.height = touch.y - self.y

            elif self.resize_part == "up":
                self.height = touch.y - self.y

            elif self.resize_part == "bottom":
                self.height = self.top - touch.y
                self.y = touch.y

            elif self.resize_part == "left":
                self.width = self.right - touch.x
                self.x = touch.x

            else:
                self.width = touch.x - self.x

            if self.width < self.min_width:
                self.width = old_width
                self.x = old_x

            if self.height < self.min_width:
                self.height = old_height
                self.y = old_y

            if self.x < self.drag_rect_x or self.right > self.drag_rect_x + self.drag_rect_width:
                self.x = old_x
                self.width = old_width

            if self.y < self.drag_rect_y or self.top > self.drag_rect_y + self.drag_rect_height:
                self.y = old_y
                self.height = old_height

        else:
            if super(CroppingRectangle, self).on_touch_move(touch):
                if self.x < self.drag_rect_x or self.right > self.drag_rect_x + self.drag_rect_width:
                    self.x = old_x
                    self.width = old_width

                if self.y < self.drag_rect_y or self.top > self.drag_rect_y + self.drag_rect_height:
                    self.y = old_y
                    self.height = old_height

    def draw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(rgba=(10 / 255, 148 / 255, 134 / 255, 0.3))
            Rectangle(size=self.size, pos=self.pos)
            Color(rgba=get_color_from_hex("#0a9486"))
            Line(rectangle=(self.x, self.y, self.width, self.height), width=2)
            Line(points=[(self.x, self.y + self.height - dp(30)), (self.x,  self.y + self.height),
                         (self.x + dp(30),  self.y + self.height)], width=4)
            Line(points=[(self.x, self.y + dp(30)), (self.x, self.y), (self.x + dp(30), self.y)], width=4)
            Line(points=[(self.x + self.width,  self.y + self.height - dp(30)), (self.x + self.width,  self.y + self.height),
                         (self.x + self.width - dp(30),  self.y + self.height)], width=4)
            Line(points=[(self.x + self.width, self.y + dp(30)), (self.x + self.width, self.y),
                         (self.x + self.width - dp(30), self.y)], width=4)

    def reset(self, pos: tuple, size: tuple):
        self.drag_rectangle = (pos[0], pos[1], size[0], size[1])
        self.pos = pos
        self.size = size

    def __init__(self, **kwargs):
        super(CroppingRectangle, self).__init__(**kwargs)

        self.bind(size=self.draw, pos=self.draw)
        self.size_hint = (None, None)
        self.min_width, self.min_height = dp(40), dp(40)

        self.touch_range = dp(20)   # range in which resizing can be triggered
        self.resizable = False  # whether the widget is being resized
        self.resize_part = None     # left_up, up, right_up etc
