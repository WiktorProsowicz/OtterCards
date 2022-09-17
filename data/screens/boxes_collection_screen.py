from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from data.flashcards.flashcard_database import FlashcardDataBase, Box
from kivy.cache import Cache
from ..classes.slider_box import SliderBox
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from ..classes.utensils import UtensilDropUp, UtensilButton
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock


class BoxesCollectionScreen(Screen):

    title_label = ObjectProperty(None)
    slider_container = ObjectProperty(None)
    slider = ObjectProperty(None)
    more_btn = ObjectProperty(None)
    main_layout = ObjectProperty(None)

    def send_to_workshop(self, slider_box):
        if hasattr(slider_box, "box"):
            Cache.append("box_workshop", "base_box", slider_box.box)
        else:
            Cache.append("box_workshop", "base_box", Box(id=None, color="c8c8c8", name="new box", nr_compartments=5))
        App.get_running_app().switch_screen("box_workshop_screen", "left")

    def choose_box(self, slider_box):
        Cache.append("box_display", "base_box", slider_box.box)
        App.get_running_app().switch_screen("box_display_screen", "left")

    def toggle_edit_mode(self, *args):
        self.edit_mode = not self.edit_mode

        if self.edit_mode:

            if self.delete_mode:
                self.toggle_edit_mode()

            for box in self.slider_boxes:
                box.unbind(on_choose=self.choose_box)
                box.bind(on_choose=self.send_to_workshop)

            self.title_label.text = "choose to edit"

            self.utensils.toggle(None, mode="close")

            self.utensils.items["edit_btn"].change_mode("chosen")

        else:

            for box in self.slider_boxes:
                box.bind(on_choose=self.choose_box)
                box.unbind(on_choose=self.send_to_workshop)

            self.title_label.text = "boxes collection"

            self.utensils.items["edit_btn"].change_mode("enabled")

    def delete_boxes(self, *args):
        boxes_to_delete = [box for box in self.slider_boxes if box.to_delete]

        if not boxes_to_delete:
            return

        else:
            database_f = Cache.get("app_info", "database_dir")

            FlashcardDataBase.delete_boxes(database_f, [box.box for box in boxes_to_delete])

            for box in boxes_to_delete:
                self.slider_boxes.remove(box)

            self.toggle_delete_mode()
            self.utensils.toggle(self.more_btn, mode="open")
            self.refresh()

    def toggle_delete_mode(self, *args):
        self.delete_mode = not self.delete_mode

        if self.delete_mode:

            if self.edit_mode:
                self.toggle_edit_mode()

            for box in self.slider_boxes:
                box.bind(on_choose=box.toggle_delete)
                box.unbind(on_choose=self.choose_box)

                # preparing opacity=0.5 style
                box.opacity = 0.5

            self.title_label.text = "click to delete"
            self.title_label.toggle_mode("deleting")
            self.title_label.bind(on_release=self.delete_boxes)

            self.utensils.toggle(None, mode="close")

            self.utensils.items["delete_btn"].change_mode("chosen")

        else:

            for box in self.slider_boxes:
                box.unbind(on_choose=box.toggle_delete)
                box.bind(on_choose=self.choose_box)

                if box.to_delete:
                    box.toggle_delete()

                # preparing opacity=1 style
                box.opacity = 1.0

            self.title_label.text = "boxes collection"
            self.title_label.toggle_mode("normal")
            self.title_label.unbind(on_release=self.delete_boxes)

            self.utensils.items["delete_btn"].change_mode("enabled")

    def on_leave(self, *args):
        self.slider_boxes.clear()
        self.slider_container.clear_widgets()

        if self.slider_container.children:
            self.empty_info()

        if self.delete_mode:
            self.toggle_delete_mode()

        if self.edit_mode:
            self.toggle_edit_mode()

        self.utensils.toggle(None, mode="close")

    def refresh(self):
        self.slider_container.clear_widgets()
        for slider_box in self.slider_boxes:
            slider_box.bind(width=slider_box.adjust_style, size=slider_box.draw)
            slider_box.bind(pos=slider_box.draw, height=self.slider_container.resize_v)
            slider_box.bind(on_choose=self.choose_box)
            self.slider_container.add_widget(slider_box)

        if len(self.slider_boxes) == 1:
            self.slider_container.add_widget(Label(opacity=0, size_hint=(0.45, None)))

        self.slider_container.resize_v()

        self.slider_container.bind(height=self.enable_disable_scroll)

        self.slider.scroll_y = 1

        self.empty_info()

    def enable_disable_scroll(self, *args):
        if self.slider_container.height > self.slider.height:
            self.slider.do_scroll_y = True
        else:
            self.slider.do_scroll_y = False

    def empty_info(self):
        # adding encouraging label in case there are no tags
        if not self.slider_boxes and self.so_empty_lbl not in self.main_layout.children:

            if self.so_empty_lbl is None:
                text = "so empty...\nconsider adding some boxes!"

                self.so_empty_lbl = Label(text=text, size_hint=(1, None),
                                          pos_hint={"center_y": 0.6, "center_x": 0.5},
                                          color=get_color_from_hex("#AAAAAA"), font_size=self.slider_container.width * 0.07)

            self.main_layout.add_widget(self.so_empty_lbl)

        elif self.so_empty_lbl in self.main_layout.children:
            self.main_layout.remove_widget(self.so_empty_lbl)

    def on_enter(self, *args):
        # initializing utensils (in on_enter because otherwise utensils might have wrong size)
        if self.utensils is None:
            self.utensils = UtensilDropUp(pos=(self.more_btn.x, -dp(10)))

            # preparing action buttons
            work_dir = Cache.get("app_info", "work_dir") + "/data/textures"
            delete_btn = UtensilButton(work_dir + "/delete_icon.png", work_dir + "/delete_icon_chosen.png",
                                       height=self.more_btn.height, width=self.more_btn.width)
            edit_btn = UtensilButton(work_dir + "/edit_icon.png", work_dir + "/edit_icon_chosen.png",
                                     height=self.more_btn.height, width=self.more_btn.width)
            add_btn = UtensilButton(work_dir + "/add_icon.png",
                                    height=self.more_btn.height, width=self.more_btn.width)

            delete_btn.bind(pos=delete_btn.draw)
            edit_btn.bind(pos=edit_btn.draw)
            add_btn.bind(pos=add_btn.draw, on_release=self.send_to_workshop)

            self.utensils.items["delete_btn"] = delete_btn
            self.utensils.items["edit_btn"] = edit_btn
            self.utensils.items["add_btn"] = add_btn

            self.more_btn.bind(on_release=self.utensils.toggle)
            self.ids["additional_layout"].add_widget(self.utensils)

        self.update_buttons()

    def update_buttons(self):

        if self.slider_boxes:
            self.utensils.items["delete_btn"].bind(on_release=self.toggle_delete_mode)
            self.utensils.items["delete_btn"].change_mode("enabled")
            self.utensils.items["edit_btn"].bind(on_release=self.toggle_edit_mode)
            self.utensils.items["edit_btn"].change_mode("enabled")

        else:
            self.utensils.items["delete_btn"].unbind(on_release=self.toggle_delete_mode)
            self.utensils.items["delete_btn"].change_mode("disabled")
            self.utensils.items["edit_btn"].unbind(on_release=self.toggle_edit_mode)
            self.utensils.items["edit_btn"].change_mode("disabled")

    def on_pre_enter(self, *args):
        database_f = Cache.get("app_info", "database_dir")
        retrieved_boxes = FlashcardDataBase.retrieve_boxes(database_f)

        retrieved_boxes.sort(key=lambda box: box.last_update, reverse=True)

        for box in retrieved_boxes:
            self.slider_boxes.append(SliderBox(box))

        Clock.schedule_once(lambda nt: self.refresh(), 0.07)

    def __init__(self, **kwargs):
        super(BoxesCollectionScreen, self).__init__(**kwargs)

        self.slider_boxes = []
        self.so_empty_lbl = None
        self.utensils = None

        self.edit_mode = False
        self.delete_mode = False
