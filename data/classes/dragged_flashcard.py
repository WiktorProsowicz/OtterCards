from kivy.uix.widget import Widget
from ..flashcards.flashcard import Flashcard
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Rectangle, RoundedRectangle, Color
from kivy.utils import get_color_from_hex
from kivy.uix.behaviors import DragBehavior
from kivy.properties import BooleanProperty
from kivy.metrics import dp
from kivy.animation import Animation


class DraggedFlashcard(DragBehavior, Widget):

    def_side = BooleanProperty(True)
    
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.old_touch = (touch.x, touch.y)
            Animation.cancel_all(self)
            
        return super(DraggedFlashcard, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.old_touch[0] - dp(3) <= touch.x <= self.old_touch[0] + dp(3) and self.old_touch[1] - dp(3) <= touch.y <= self.old_touch[1] + dp(3):
            self.def_side = not self.def_side

        if self.x <= self.drag_rect_x - self.width * 0.1:
            self.dispatch("on_incorrect")

        if self.right >= self.drag_rect_x + self.drag_rect_width + self.width * 0.1:
            self.dispatch("on_correct")
            
        return super(DraggedFlashcard, self).on_touch_up(touch)
    
    def on_touch_move(self, touch):
        old_pos = (self.x, self.y)

        ret = super(DraggedFlashcard, self).on_touch_move(touch)

        if self.top >= self.drag_rect_y + self.drag_rect_height or self.y <= self.drag_rect_y:
            self.pos = old_pos

        if self.x <= self.drag_rect_x - self.width * 0.1:
            self.bg_color = "#d67e5c"

        elif self.right >= self.drag_rect_x + self.drag_rect_width + self.width * 0.1:
            self.bg_color = "#5ad1a5"

        else:
            self.bg_color = "#edebda"

        return ret

    def adjust_style(self, *args):

        self.width = self.max_size[0]
        font_size = self.width * 0.07
        self.padding = self.width * 0.05

        hidden_text, def_text = "", ""
        for line in self.flashcard.hidden_lines:
            hidden_text += line + "\n"
        for line in self.flashcard.def_lines:
            def_text += line + "\n"

        hidden_text = hidden_text.rstrip()
        def_text = def_text.rstrip()

        self.hidden_lbl = CoreLabel(text=hidden_text, font_size=font_size, text_size=(self.width - self.padding*2, None))
        self.def_lbl = CoreLabel(text=def_text, font_size=font_size, text_size=(self.width - self.padding*2, None))
        self.hidden_lbl.refresh()
        self.def_lbl.refresh()

        while max(self.def_lbl.texture.height, self.hidden_lbl.texture.height) + self.padding * 2 > self.max_size[1]:
            font_size *= 0.95

            self.hidden_lbl = CoreLabel(text=hidden_text, font_size=font_size, text_size=(self.width - self.padding*2, None))
            self.def_lbl = CoreLabel(text=def_text, font_size=font_size, text_size=(self.width - self.padding*2, None))
            self.hidden_lbl.refresh()
            self.def_lbl.refresh()

        self.height = max(self.def_lbl.texture.height, self.hidden_lbl.texture.height) + self.padding * 2

    def reset(self, pos: tuple, def_side: bool):

        self.adjust_style()
        self.def_side = def_side
        self.pos = pos
        self.bg_color = "#edebda"
        self.opacity = 1

    def draw(self, *args):

        lbl = self.def_lbl if self.def_side else self.hidden_lbl

        self.canvas.clear()
        with self.canvas:
            Color(rgba=get_color_from_hex(self.bg_color))
            RoundedRectangle(size=self.size, pos=self.pos)

            Color(rgba=get_color_from_hex("#444444"))
            Rectangle(size=(lbl.texture.width, lbl.texture.height),
                      pos=(self.x + self.width / 2 - lbl.texture.width / 2, self.y + self.height / 2 - lbl.texture.height / 2),
                      texture=lbl.texture)

    def on_correct(self, *args):
        pass

    def on_incorrect(self, *args):
        pass

    def __init__(self, max_size: tuple, **kwargs):
        super(DraggedFlashcard, self).__init__(**kwargs)

        self.max_size = max_size
        self.size_hint = (None, None)

        self.flashcard: Flashcard = None

        self.bind(pos=self.draw, size=self.draw, def_side=self.draw)

        self.def_lbl = CoreLabel(text="")
        self.hidden_lbl = CoreLabel(text="")

        self.def_lbl.refresh()
        self.hidden_lbl.refresh()

        self.padding = 0
        self.bg_color = "#edebda"
        
        self.old_touch = (0, 0)

        self.register_event_type("on_correct")
        self.register_event_type("on_incorrect")
