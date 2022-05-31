from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from kivy.app import App
from kivy.properties import ObjectProperty
from ..flashcards.flashcard_database import FlashcardDataBase, LengthError, UniqueNameError
from ..classes.popups import ok_popup, yes_no_popup


class BoxWorkshopScreen(Screen):

    title_label = ObjectProperty(None)
    base_box_widget = ObjectProperty(None)
    decrease_btn = ObjectProperty(None)
    increase_btn = ObjectProperty(None)
    comps_increaser = ObjectProperty(None)
    is_special_btn = ObjectProperty(None)
    name_input = ObjectProperty(None)
    red_slider = ObjectProperty(None)
    green_slider = ObjectProperty(None)
    blue_slider = ObjectProperty(None)
    color_label = ObjectProperty(None)

    def save(self):

        base_box = self.base_box_widget.box
        database_f = Cache.get("app_info", "database_dir")

        try:
            FlashcardDataBase.insert_box(database_f, base_box)

        except UniqueNameError:
            warning_pop = ok_popup("this name is taken!", self.width, 0.3)
            warning_pop.open()

        except LengthError:
            warning_pop = ok_popup("this name has invalid length!", self.width, 0.3)
            warning_pop.open()

        else:
            App.get_running_app().switch_screen("previous", "inverted")

    def leave_workshop(self, mode):
        base_info = [self.base_box_widget.box.name, self.base_box_widget.box.color,
                     self.base_box_widget.box.nr_compartments, self.base_box_widget.box.is_special]

        if base_info == self.init_info and mode != "save":
            App.get_running_app().switch_screen("boxes_collection_screen", "right")

        elif mode == "back":

            info_pop = yes_no_popup("do you want to save changes?", self.width, 0.3, lambda obj: self.save(),
                                    lambda obj: App.get_running_app().switch_screen("previous", "inverted"))
            info_pop.open()

        else:
            self.save()

    def unable_disable_changes(self, btn=None, state=None):

        if self.base_box_widget.box.is_special or self.base_box_widget.box.id is not None:
            self.comps_increaser.value = 1 if self.base_box_widget.box.is_special else self.base_box_widget.box.nr_compartments
            self.comps_increaser.opacity = 0.5
            self.increase_btn.opacity = 0.5
            self.decrease_btn.opacity = 0.5
            self.decrease_btn.disabled = True
            self.increase_btn.disabled = True

            self.decrease_btn.unbind(on_release=self.comps_increaser.decrease)
            self.increase_btn.unbind(on_release=self.comps_increaser.increase)
            self.comps_increaser.unbind(value=self.base_box_widget.change_nr_compartments)

        else:
            self.comps_increaser.value = self.base_box_widget.box.nr_compartments
            self.comps_increaser.opacity = 1
            self.increase_btn.opacity = 1
            self.decrease_btn.opacity = 1
            self.decrease_btn.disabled = False
            self.increase_btn.disabled = False

            self.decrease_btn.bind(on_release=self.comps_increaser.decrease)
            self.increase_btn.bind(on_release=self.comps_increaser.increase)
            self.comps_increaser.bind(value=self.base_box_widget.change_nr_compartments)

    def on_enter(self, *args):
        self.base_box_widget.refresh()

        # user is not allowed to change "is special" if box is not new
        if self.base_box_widget.box.id is not None:
            self.is_special_btn.disabled = True
            self.is_special_btn.opacity = 0.5
        else:
            self.is_special_btn.disabled = False
            self.is_special_btn.opacity = 1

        # setting initial button state according to base box
        self.is_special_btn.state = "down" if self.base_box_widget.box.is_special else "normal"

        self.unable_disable_changes()

        self.is_special_btn.bind(state=self.unable_disable_changes)

    def update_color_label(self):
        self.color_label.text = "color #" + self.base_box_widget.box.color

    def on_pre_enter(self, *args):

        base_box = Cache.get("box_workshop", "base_box")

        self.title_label.text = "edit box" if base_box.id is not None else "create box"

        self.init_info = [base_box.name, base_box.color, base_box.nr_compartments, base_box.is_special]

        self.base_box_widget.box = base_box

        init_col = self.base_box_widget.box.color
        r, g, b = init_col[0:2], init_col[2:4], init_col[4:6]
        r, g, b = int("0x" + r, 16), int("0x" + g, 16), int("0x" + b, 16)

        self.red_slider.value = r
        self.green_slider.value = g
        self.blue_slider.value = b

        self.name_input.text = self.base_box_widget.box.name

        self.color_label.text = "color #" + self.base_box_widget.box.color

        if not self.settings_bound:
            self.red_slider.bind(value=lambda slider, value: self.base_box_widget.change_color("red", int(value)))
            self.green_slider.bind(value=lambda slider, value: self.base_box_widget.change_color("green", int(value)))
            self.blue_slider.bind(value=lambda slider, value: self.base_box_widget.change_color("blue", int(value)))

            self.red_slider.bind(value=lambda slider, value: self.update_color_label())
            self.green_slider.bind(value=lambda slider, value: self.update_color_label())
            self.blue_slider.bind(value=lambda slider, value: self.update_color_label())

            self.name_input.bind(text=lambda text_input, text: self.base_box_widget.change_name(text))

            self.is_special_btn.bind(state=lambda btn, state: self.base_box_widget.change_special(state == "down"))

            self.settings_bound = True

    def __init__(self, **kwargs):
        super(BoxWorkshopScreen, self).__init__(**kwargs)

        # information about edited box
        self.init_info = False

        self.settings_bound = False     # whether there are lambda functions bound to sliders etc
