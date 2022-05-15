from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.properties import BooleanProperty


class SmartInput(TextInput):
    marked = BooleanProperty(False)  # whether the input is checked by holding it

    def toggle_marked(self, *args):
        self.marked = not self.marked

        if not self.marked:
            self.background_disabled_normal = self.background_normal
            self.disabled = not self.to_edit

        else:
            self.background_disabled_normal = self.background_marked
            self.disabled = True

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            Clock.schedule_once(self._do_hold, .5)
            touch.grab(self)
            return super(SmartInput, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            Clock.unschedule(self._do_hold)
            touch.ungrab(self)

    def _do_hold(self, dt):
        self.dispatch("on_hold")

    def on_hold(self):
        pass

    def resize(self, *args):
        self.font_size = self.width / 18

        self.text = self.text.replace("\n", "")  # making sure that line_wrap is True but still there is only one line

        nr_lines = len(self._split_smart(self.text)[0])  # getting number of line-split parts to properly resize

        self.height = self.padding[1] * 2 + nr_lines * self.line_height

    def __init__(self, background_marked: str, **kwargs):
        super(SmartInput, self).__init__(**kwargs)

        self.register_event_type("on_hold")

        self.background_marked = background_marked
        self.background_disabled_normal = self.background_normal

        self.to_edit = True   # whether we can write something into input, attr used in dict waiting room for defaultly disabled
