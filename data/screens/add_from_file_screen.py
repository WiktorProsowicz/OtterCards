from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from ..classes.horizontal_slider_tag import HorizontalSliderTag
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from ..classes.smart_grid_layout import SmartGridLayout
from kivy.cache import Cache
from kivy.effects.scroll import ScrollEffect
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from data.flashcards.flashcard_database import FlashcardDataBase
from ..classes.slider_tag import SliderTag
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from ..data_processing import get_cards_from_file
from kivy.app import App
from ..classes.popups import loading_popup, ok_popup, tags_popup


class AddFromFileScreen(Screen):
    filename_label = ObjectProperty(None)
    tags_slider = ObjectProperty(None)
    tags_container = ObjectProperty(None)
    add_tags_btn = ObjectProperty(None)
    choose_file_btn = ObjectProperty(None)
    hidden_input = ObjectProperty(None)
    def_input = ObjectProperty(None)
    title_label = ObjectProperty(None)
    main_layout = ObjectProperty(None)

    def submit(self):

        if self.selected_file is None:
            warning_pop = ok_popup("you have to choose a file before processing", self.width, 0.9 / 2.5)

            warning_pop.open()

        else:
            loading_pop = loading_popup("collecting cards...", self.width)
            loading_pop.open()

            Clock.schedule_once(lambda nt: self.pre_save_cards(), .2)
            Clock.schedule_once(lambda nt: loading_pop.dismiss(), .2)

    def pre_save_cards(self):
        hidden_pattern = self.hidden_input.get_pattern()
        def_pattern = self.def_input.get_pattern()
        aux_database_f = Cache.get("app_info", "aux_database_dir")

        retrieved_cards = get_cards_from_file(self.selected_file, hidden_pattern, def_pattern)
        tags = [slider_tag.tag.name for slider_tag in self.slider_tags]

        for card in retrieved_cards:
            card.tags = tags.copy()

        # inserting to aux database will assign new ids to flashcards and with this we can ensure that the cards waiting
        # room will handle original ones

        FlashcardDataBase.insert_cards(aux_database_f, retrieved_cards)

        Cache.append("card_waiting_room", "card_ids", [card.id for card in retrieved_cards])

        App.get_running_app().switch_screen("card_waiting_room_screen", "left")

    def select_file(self, selection):
        # /// VALIDATION MAY BE NEEDED!

        if not selection:
            return

        self.selected_file = selection[0]
        self.filename_label.text = selection[0]

    def show_files(self):
        workdir = Cache.get("app_info", "work_dir")
        rootpath = Cache.get("app_info", "rootpath")

        # preparing file_chooser popup
        # filechooser progress is "muted" in main_layout.kv by setting opacity to 0
        pop_content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        filechooser = FileChooserIconView(filters=["*.txt", "*.ocb"], size_hint=(1, 0.9), rootpath=rootpath, show_hidden=True)
        filechooser_popup = Popup(title="choose file", title_align="center", separator_color=(0, 0, 0, 1),
                                  size_hint=(0.9, 0.6), title_color=get_color_from_hex("#444444"),
                                  background=workdir + "/data/textures/popup_background.png",
                                  title_size=self.title_label.font_size, content=pop_content,
                                  border=[0, 0, 0, 0])

        btn = Button(text="submit", color=get_color_from_hex("#444444"),
                     font_size=self.title_label.font_size * 0.8,
                     background_normal=workdir + "/data/textures/yes_button_normal.png",
                     background_down=workdir + "/data/textures/yes_button_down.png", opacity=0.7,
                     size_hint=(0.5, None), pos_hint={"center_x": 0.5}, height=self.title_label.font_size)

        pop_content.add_widget(filechooser)
        pop_content.add_widget(btn)

        btn.height = btn.font_size * 2.5

        btn.bind(on_release=lambda btn: self.select_file(filechooser.selection))
        btn.bind(on_release=filechooser_popup.dismiss)

        filechooser_popup.open()

    def show_tags(self):

        # preparing tag popup
        database_dir = Cache.get("app_info", "database_dir")

        not_names = [slider_tag.tag.name for slider_tag in self.slider_tags]
        tags_pop = tags_popup("choose tag", self.size, database_dir, self.add_tag, "there are no tags left", not_names)
        tags_pop.open()

    def add_tag(self, v_slider_tag):
        if v_slider_tag.tag.name not in [slider_tag.tag.name for slider_tag in self.slider_tags]:
            h_slider_tag = HorizontalSliderTag(v_slider_tag.tag)
            self.slider_tags.append(h_slider_tag)

            self.refresh_tags()

    def refresh_tags(self):

        self.tags_container.clear_widgets()
        for tag in self.slider_tags:
            self.tags_container.add_widget(tag)
            tag.bind(pos=tag.adjust_style, height=tag.adjust_style)
            tag.bind(width=self.tags_container.resize_h, size=tag.draw, pos=tag.draw)

        self.tags_container.resize_h()

        Clock.schedule_once(self.enable_disable_scroll, -1)

    def enable_disable_scroll(self, *args):
        self.tags_slider.do_scroll_x = True if self.tags_container.width > self.tags_slider.width else False

    def on_leave(self, *args):

        self.slider_tags.clear()
        self.tags_container.clear_widgets()

    def on_pre_enter(self, *args):

        # restoring labels and inputs
        self.selected_file = None
        self.filename_label.text = "no files chosen yet"

        self.hidden_input.text = "*[hidden line]"
        self.hidden_input.old_text = "*[hidden line]"
        self.def_input.text = "[def line]"
        self.def_input.old_text = "[def line]"

        if self.def_input.immutable is None:
            self.def_input.immutable = "[def line]"
        if self.hidden_input.immutable is None:
            self.hidden_input.immutable = "[hidden line]"

        self.def_input.bind(text=self.def_input.validate_text)
        self.hidden_input.bind(text=self.hidden_input.validate_text)

    def __init__(self, **kwargs):
        super(AddFromFileScreen, self).__init__(**kwargs)

        self.slider_tags = []

        self.selected_file = None  # path to currently selected file
        self.selected_language_mode = None  # string containing language_mode passed to get_from_dictionary function
