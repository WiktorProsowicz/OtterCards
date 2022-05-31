from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.utils import get_color_from_hex
from data.flashcards.flashcard_database import Flashcard
from kivy.animation import AnimationTransition, Animation
from kivy.properties import BooleanProperty
from kivy.clock import Clock


class SliderCard(Widget):

    marked = BooleanProperty(False)

    def toggle_label(self, *args):
        self.to_label = not self.to_label

        if not self.to_label:
            self.opacity = 0.5
            self.background_color = "#6de3c0"
            self.draw()

        else:
            self.opacity = 1
            self.background_color = "#33b5af"
            self.draw()

    def toggle_delete(self, *args):
        self.to_delete = not self.to_delete

        if not self.to_delete:
            self.opacity = 0.5
            self.background_color = "#6de3c0"
            self.draw()

        else:
            self.opacity = 1
            self.background_color = "#ab0202"
            self.draw()

    def toggle_marked(self, *args):
        self.marked = not self.marked

        if not self.marked:
            self.background_color = "6de3c0"

        else:
            self.background_color = "d48f5b"

        self.draw()

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            Clock.schedule_once(self._do_hold, .15)     # card is held after specific time
            Clock.schedule_once(lambda nt: touch.ungrab(self), .15)  # after specific time touch up won't trigger on_choose
            touch.grab(self)
            return super(SliderCard, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.dispatch("on_choose")
            Clock.unschedule(self._do_hold)
            return super(SliderCard, self).on_touch_up(touch)

    def _do_hold(self, nt):
        self.dispatch("on_hold")

    def on_hold(self):
        pass

    def on_choose(self):
        pass

    def toggle_short_long(self, *args):

        self.shortened = not self.shortened
        self.adjust_style()

    def adjust_style(self, *args):

        # making new labels because we can't give it a font size other way
        if self.shortened:
            self.def_label = CoreLabel(text=self.def_text_s, font_size=self.width / 22)
            self.hidden_label = CoreLabel(text=self.hidden_text_s, font_size=self.width / 22)

        else:
            self.def_label = CoreLabel(text=self.def_text.rstrip("\n"), font_size=self.width / 22)
            self.hidden_label = CoreLabel(text=self.hidden_text.rstrip("\n"), font_size=self.width / 22)

        self.tags = CoreLabel(text=self.tags_text, font_size=self.width / 22, split_str="  ")

        for label in [self.def_label, self.hidden_label, self.tags]:

            label.text_size = (None, None)  # resetting the text size to get real texture size
            label.refresh()

            if not self.shortened and label.texture.width > self.width * 0.94 - 2 * self.std_spacing:
                label.text_size = (self.width * 0.94 - 2 * self.std_spacing, None)
                label.refresh()

            if self.shortened and label.texture.width > self.width * 0.94 - 2 * self.std_spacing:
                label.text += "..."
                while label.texture.width > self.width * 0.94 - 2 * self.std_spacing:
                    label.text = label.text[:-4]
                    label.text += "..."
                    label.refresh()

        dest_height = self.spacing + self.def_label.texture.height + self.hidden_label.texture.height + \
                      self.tags.texture.height + self.std_spacing * 7 + self.width * 0.06

        anim = Animation(height=dest_height, duration=.1, transition=AnimationTransition.linear)
        anim.bind(on_progress=lambda anim, wid, prog: self.draw())
        anim.start(self)

    def draw(self, *args):

        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=get_color_from_hex(self.background_color))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[(20, 20), (20, 20), (20, 20), (20, 20)])

            Color(rgba=get_color_from_hex("#109e82"))
            RoundedRectangle(
                pos=(self.x + self.width * 0.03,
                     self.y + self.width * 0.03 + self.tags.texture.height + self.std_spacing * 6 + self.def_label.texture.height),
                size=(self.hidden_label.texture.width + 2 * self.std_spacing,
                      self.hidden_label.texture.height + 2 * self.std_spacing),
                radius=[(5, 5), (5, 5), (5, 5), (5, 5)])
            Color(rgba=get_color_from_hex("#333333"))
            Rectangle(size=(self.hidden_label.texture.width, self.hidden_label.texture.height),
                      pos=(self.x + self.width * 0.03 + self.std_spacing,
                           self.y + self.width * 0.03 + self.tags.texture.height + self.std_spacing * 7 + self.def_label.texture.height),
                      texture=self.hidden_label.texture)

            Color(rgba=get_color_from_hex("#04c29c"))
            RoundedRectangle(
                pos=(self.x + self.width * 0.03,
                     self.y + self.width * 0.03 + self.tags.texture.height + self.std_spacing * 3),
                size=(self.def_label.texture.width + 2 * self.std_spacing,
                      self.def_label.texture.height + 2 * self.std_spacing),
                radius=[(5, 5), (5, 5), (5, 5), (5, 5)])
            Color(rgba=get_color_from_hex("#333333"))
            Rectangle(size=(self.def_label.texture.width, self.def_label.texture.height),
                      pos=(self.x + self.width * 0.03 + self.std_spacing,
                           self.y + self.width * 0.03 + self.tags.texture.height + self.std_spacing * 4),
                      texture=self.def_label.texture)

            Color(rgba=get_color_from_hex("#09876e"))
            RoundedRectangle(
                pos=(self.x + self.width * 0.03, self.y + self.width * 0.03),
                size=(self.tags.texture.width + 2 * self.std_spacing,
                      self.tags.texture.height + 2 * self.std_spacing),
                radius=[(5, 5), (5, 5), (5, 5), (5, 5)])
            Color(rgba=get_color_from_hex("#CCCCCC"))
            Rectangle(size=(self.tags.texture.width, self.tags.texture.height),
                      pos=(self.x + self.width * 0.03 + self.std_spacing,
                           self.y + self.std_spacing + self.width * 0.03),
                      texture=self.tags.texture)

        if not self.shortened:
            with self.canvas.before:
                Color(rgba=get_color_from_hex("#0e7d52"))
                Line(width=2, rounded_rectangle=(self.x + 1, self.y + 1, self.width - 2, self.height - 2, 20))

        if self.flashcard.is_redundant:
            dev_label = CoreLabel(text="R", font_size=self.width / 20)
            dev_label.refresh()

            with self.canvas.before:
                Color(rgb=get_color_from_hex("#8f3b1f"))
                Rectangle(size=(dev_label.texture.width, dev_label.texture.height),
                          pos=(self.right - dev_label.texture.height - dp(5),
                               self.top - dev_label.texture.height - dp(5)),
                          texture=dev_label.texture)

    def refresh_info(self):
        self.def_text, self.hidden_text, self.tags_text = "", "", ""
        self.def_text_s, self.hidden_text_s = "", ""
        for nr, line in enumerate(self.flashcard.hidden_lines, 1):
            self.hidden_text_s += f"{nr}. {line} "
            self.hidden_text += f"{nr}. {line} \n"

        for nr, line in enumerate(self.flashcard.def_lines, 1):
            self.def_text_s += f"{nr}. {line} "
            self.def_text += f"{nr}. {line} \n"

        for tag in self.flashcard.tags:
            self.tags_text += f"#{tag}  "

    def __init__(self, flashcard: Flashcard, **kwargs):
        super(SliderCard, self).__init__(**kwargs)

        self.spacing = dp(5)

        self.flashcard = flashcard  # Flashcard instance to carry important info

        self.size_hint = (1, None)
        self.background_color = "#6de3c0"

        self.def_label = CoreLabel(text="xxx")
        self.hidden_label = CoreLabel(text="xxx")
        self.tags = CoreLabel(text="xxx")

        self.def_label.refresh()
        self.hidden_label.refresh()
        self.tags.refresh()

        self.shortened = True
        self.to_delete = False
        self.to_label = False

        self.std_spacing = dp(5)    # spacing for drawing

        self.register_event_type("on_choose")
        self.register_event_type("on_hold")

        # long and shortened versions of core_labels texts displayed on card
        self.def_text, self.hidden_text, self.tags_text = "", "", ""
        self.def_text_s, self.hidden_text_s = "", ""

        # generate new texts based on self.flashcard
        self.refresh_info()
