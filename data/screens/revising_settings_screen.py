from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from ..classes.popups import boxes_popup
from kivy.cache import Cache
from ..flashcards.flashcard_database import FlashcardDataBase
from kivy.clock import Clock
from ..classes.slider_box import SliderBox
from kivy.uix.label import Label
from ..classes.popups import revising_parameters_popup
from kivy.app import App


class RevisingSettingsScreen(Screen):

    normal_box = ObjectProperty(None)
    normal_box_cnt = ObjectProperty(None)
    special_box = ObjectProperty(None)
    special_box_cnt = ObjectProperty(None)
    increaser = ObjectProperty(None)
    increase_btn = ObjectProperty(None)
    decrease_btn = ObjectProperty(None)
    dump_boxes_cnt = ObjectProperty(None)
    boxes_slider = ObjectProperty(None)
    special_mode_btn = ObjectProperty(None)
    normal_mode_btn = ObjectProperty(None)
    carousel = ObjectProperty(None)

    def choose_mode(self, *args):
        if self.carousel.index == 0:

            Cache.append("revising", "box", self.normal_box.box.id)
            Cache.append("revising", "compartment", self.increaser.value)

        else:
            Cache.append("revising", "box", self.special_box.box.id)
            Cache.append("revising", "dump_boxes", [box.box for box in self.dump_boxes if box.marked])

        revising_pop = revising_parameters_popup(self.size, Cache.get("app_info", "work_dir"),
                                                 lambda btn, state: Cache.append("revising", "show_def", state == "down"),
                                                 lambda btn: App.get_running_app().switch_screen("revising_screen", "left"))
        revising_pop.open()

    def on_slide_change(self, index):

        if index == 0:
            self.ids["first_dot"].state = "down"
            self.ids["second_dot"].state = "normal"

        elif index == 1:
            self.ids["first_dot"].state = "normal"
            self.ids["second_dot"].state = "down"

    def update_btns(self, *args):

        if self.normal_box.box is None:
            self.increase_btn.opacity = 0.5
            self.increase_btn.unbind(on_release=self.increaser.increase)
            self.decrease_btn.opacity = 0.5
            self.decrease_btn.unbind(on_release=self.increaser.decrease)
            return

        if self.increaser.value == 1:
            self.increase_btn.opacity = 1
            self.decrease_btn.opacity = 0.3

        elif self.increaser.value == self.normal_box.box.nr_compartments:
            self.increase_btn.opacity = 0.3
            self.decrease_btn.opacity = 1

        else:
            self.increase_btn.opacity = 1
            self.decrease_btn.opacity = 1

        self.increase_btn.bind(on_release=self.increaser.increase)
        self.decrease_btn.bind(on_release=self.increaser.decrease)

    def choose_normal_box(self, box):
        self.normal_box.box = box
        self.normal_box.refresh()

        if box is not None:
            self.increaser.value = 1
            self.increaser.max_value = box.nr_compartments

            self.normal_mode_btn.bind(on_release=self.choose_mode)
            self.normal_mode_btn.opacity = 1

        else:
            self.increaser.value = -1

            self.normal_mode_btn.unbind(on_release=self.choose_mode)
            self.normal_mode_btn.opacity = 0.5

    def choose_special_box(self, box):
        self.special_box.box = box
        self.special_box.refresh()

        for box in self.dump_boxes:
            if box.marked:
                box.toggle_marked()

        if box is None:
            self.special_mode_btn.unbind(on_release=self.choose_mode)
            self.special_mode_btn.opacity = 0.5

        else:
            self.special_mode_btn.bind(on_release=self.choose_mode)
            self.special_mode_btn.opacity = 1

    def show_normal_boxes(self):
        database_f = Cache.get("app_info", "database_dir")

        box_pop = boxes_popup("choose box", self.size, database_f, lambda box: self.choose_normal_box(box.box),
                              "there are no boxes to choose from", "normal")
        box_pop.open()

    def show_special_boxes(self):
        database_f = Cache.get("app_info", "database_dir")

        box_pop = boxes_popup("choose box", self.size, database_f, lambda box: self.choose_special_box(box.box),
                              "there are no boxes to choose from", "special")
        box_pop.open()

    def refresh_dump_boxes(self):
        self.dump_boxes_cnt.clear_widgets()
        for slider_box in self.dump_boxes:
            if slider_box.marked:
                slider_box.toggle_marked()

            slider_box.bind(width=slider_box.adjust_style, size=slider_box.draw)
            slider_box.bind(pos=slider_box.draw, height=self.dump_boxes_cnt.resize_v)
            slider_box.bind(on_choose=slider_box.toggle_marked)
            self.dump_boxes_cnt.add_widget(slider_box)

        if len(self.dump_boxes) == 1:
            self.dump_boxes_cnt.add_widget(Label(opacity=0, size_hint=(0.45, None)))

        self.dump_boxes_cnt.resize_v()

        self.boxes_slider.scroll_y = 1

    def on_leave(self, *args):
        self.dump_boxes.clear()

    def on_pre_enter(self, *args):
        database_f = Cache.get("app_info", "database_dir")
        retrieved_boxes = FlashcardDataBase.retrieve_boxes(database_f)

        normal_boxes = [box for box in retrieved_boxes if not box.is_special]
        special_boxes = [box for box in retrieved_boxes if box.is_special]

        for box in normal_boxes:
            self.dump_boxes.append(SliderBox(box))

        self.increaser.bind(value=self.update_btns)

        self.normal_box_cnt.clear_widgets()
        self.special_box_cnt.clear_widgets()

        if normal_boxes:
            self.normal_box_cnt.add_widget(self.normal_box)

            normal_boxes.sort(key=lambda box: box.last_update, reverse=True)

            Clock.schedule_once(lambda nt: self.choose_normal_box(normal_boxes[0]), 0.07)

        else:
            Clock.schedule_once(lambda nt: self.choose_normal_box(None), 0.07)

        if special_boxes:
            self.special_box_cnt.add_widget(self.special_box)

            special_boxes.sort(key=lambda box: box.last_update, reverse=True)

            Clock.schedule_once(lambda nt: self.choose_special_box(special_boxes[0]), 0.07)

        else:
            Clock.schedule_once(lambda nt: self.choose_special_box(None), 0.07)

        Clock.schedule_once(lambda nt: self.refresh_dump_boxes(), 0.07)

    def __init__(self, **kwargs):
        super(RevisingSettingsScreen, self).__init__(**kwargs)

        self.dump_boxes = []