from kivy.properties import ObjectProperty
from .add_from_file_screen import AddFromFileScreen
from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from kivy.utils import get_color_from_hex
from kivy.uix.popup import Popup
from kivy.effects.scroll import ScrollEffect
from ..classes.smart_grid_layout import SmartGridLayout
from ..classes.slider_language_mode import SliderLanguageMode
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from ..data_processing import get_cards_from_dictionary
from data.flashcards.flashcard_database import FlashcardDataBase
from kivy.app import App
from ..classes.popups import ok_popup, loading_popup
from ..extracting_from_dictionaries import get_dictionary_from_language_mode
from kivy.clock import Clock


class AddFromDictionaryScreen(Screen):
    """
    This class is an extension of AddFromFileScreen class and most methods are called directly from "parent" to avoid
    copying big chunks of code. Several methods are not copied:
    submit: in this class it works differently
    pre_save_cards: as above
    on_pre_enter: in "parent" class there were used attributes not present in here
    Not using inheritance because it's causing duplication of kv features in layout.
    For details in methods usage see AddFromFileScreen
    """

    filename_label = ObjectProperty(None)
    tags_slider = ObjectProperty(None)
    tags_container = ObjectProperty(None)
    add_tags_btn = ObjectProperty(None)
    choose_file_btn = ObjectProperty(None)
    title_label = ObjectProperty(None)
    main_layout = ObjectProperty(None)
    cards_increaser = ObjectProperty(None)
    subdefs_increaser = ObjectProperty(None)
    language_mode = ObjectProperty(None)
    get_hinted_button = ObjectProperty(None)
    word_input = ObjectProperty(None)

    def show_language_modes(self):
        # preparing tag popup
        modes_container = SmartGridLayout(cols=2, size_hint=(1, None), spacing=dp(10))
        slider = ScrollView(size=(self.main_layout.width * 0.9, self.main_layout.height * 0.5),
                            do_scroll_x=False, effect_y=ScrollEffect(), bar_inactive_color=(0, 0, 0, 0),
                            pos_hint={"y": 0})

        workdir = Cache.get("app_info", "work_dir")

        slider.add_widget(modes_container)

        modes_popup = Popup(title="choose mode", auto_dismiss=True,
                            size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                            title_color=get_color_from_hex("#444444"),
                            background=workdir + "/data/textures/popup_background.png",
                            title_size=self.title_label.font_size * 0.9, content=slider,
                            border=[0, 0, 0, 0])
        modes_popup.height += slider.height + dp(20)

        modes = ["polish_to_german", "polish_to_english", "english_to_polish", "german_to_polish",
                 "english_to_arabic", "arabic_to_english", "english_to_danish", "danish_to_english",
                 "english_to_dutch", "dutch_to_english", "english_to_finnish", "finnish_to_english",
                 "english_to_german", "german_to_english", "english_to_greek", "greek_to_english",
                 "english_to_hindi", "hindi_to_english", "english_to_norwegian", "norwegian_to_english",
                 "english_to_italian", "italian_to_english", "english_to_portuguese", "portuguese_to_english",
                 "russian_to_english", "english_to_russian", "english_to_spanish", "spanish_to_english",
                 "english_to_swedish", "swedish_to_english", "english_to_turkish", "turkish_to_english",
                 "english_to_chinese", "chinese_to_english"]
        modes.sort()

        for mode in modes:
            slider_mode = SliderLanguageMode(mode, size_hint=(0.4, None))
            slider_mode.bind(width=lambda obj, width: obj.draw(), pos=lambda obj, pos: obj.draw())
            slider_mode.bind(width=lambda obj, width: modes_container.resize_v(),
                             on_choose=self.change_language_mode)
            slider_mode.bind(on_choose=lambda obj: modes_popup.dismiss())
            modes_container.add_widget(slider_mode)

        modes_container.resize_v()

        if modes_container.height > slider.height:
            slider.do_scroll_y = True
        else:
            slider.do_scroll_y = False
        slider.scroll_y = 1

        modes_popup.open()

    def change_language_mode(self, slider_mode):
        self.language_mode.language_mode = slider_mode.language_mode
        self.language_mode.draw()

    def submit(self):

        if self.language_mode.language_mode is None:
            warning_pop = ok_popup("you have to choose languages before processing", self.width, 0.9 / 2.5)

            warning_pop.open()

        elif self.pages.page == 1 and self.word_input.text == "":
            warning_pop = ok_popup("you have to pass a word before processing", self.width, 0.9 / 2.5)

            warning_pop.open()

        elif self.pages.page == 0 and self.selected_file is None:

            warning_pop = ok_popup("you have to choose a file before processing", self.width, 0.9 / 2.5)

            warning_pop.open()

        else:

            loading_pop = loading_popup("collecting cards...", self.width)

            loading_pop.open()

            Clock.schedule_once(lambda nt: self.pre_save_cards(), .2)

            Clock.schedule_once(lambda nt: loading_pop.dismiss(), .2)

    def pre_save_cards(self):

        tagnames = [tag.tag.name for tag in self.slider_tags]

        subdefs_limit = self.subdefs_increaser.value if self.subdefs_increaser.value > -1 else None
        cards_limit = self.cards_increaser.value if self.cards_increaser.value > -1 else None
        get_hinted = True if self.get_hinted_button.state == "down" else False
        language_mode = self.language_mode.language_mode

        Cache.append("dict_waiting_room", "dictionary", get_dictionary_from_language_mode(language_mode))

        if self.pages.page == 0:
            retrieved_cards, extras, exceptions = get_cards_from_dictionary(self.selected_file, language_mode,
                                                                            subdefs_limit,
                                                                            cards_limit, get_hinted)
        else:
            retrieved_cards, extras, exceptions = get_cards_from_dictionary("", language_mode,
                                                                            subdefs_limit,
                                                                            cards_limit, get_hinted,
                                                                            words=[self.word_input.text])

        for card in retrieved_cards:
            card.tags = tagnames.copy()

        # inserting cards into aux database
        aux_database_f = Cache.get("app_info", "aux_database_dir")
        FlashcardDataBase.insert_cards(aux_database_f, retrieved_cards)

        Cache.append("dict_waiting_room", "card_ids", [card.id for card in retrieved_cards])
        Cache.append("dict_waiting_room", "extras", extras)
        Cache.append("dict_waiting_room", "exceptions", exceptions)

        Cache.append("dict_waiting_room", "language_mode", language_mode)
        Cache.append("dict_waiting_room", "subdefs_limit", subdefs_limit)
        Cache.append("dict_waiting_room", "cards_limit", cards_limit)
        Cache.append("dict_waiting_room", "get_hinted", get_hinted)

        App.get_running_app().switch_screen("dict_waiting_room_screen", "left")

    def select_file(self, filepath):
        AddFromFileScreen.select_file(self, filepath)

    def show_files(self):
        AddFromFileScreen.show_files(self)

    def show_tags(self):
        AddFromFileScreen.show_tags(self)

    def add_tag(self, v_slider_tag):
        AddFromFileScreen.add_tag(self, v_slider_tag)

    def refresh_tags(self):
        AddFromFileScreen.refresh_tags(self)

    def on_leave(self, *args):
        AddFromFileScreen.on_leave(self)

    def enable_disable_scroll(self, *args):
        AddFromFileScreen.enable_disable_scroll(self)

    def on_pre_enter(self, *args):
        # restoring labels and inputs
        self.selected_file = None
        self.filename_label.text = "no files chosen yet"

        self.pages.page = 1

        Clock.schedule_once(lambda nt: self.cards_increaser.draw(), 0.07)
        Clock.schedule_once(lambda nt: self.subdefs_increaser.draw(), 0.07)
        Clock.schedule_once(lambda nt: self.language_mode.draw(), 0.07)

    def on_enter(self, *args):
        self.cards_increaser.value = 3
        self.subdefs_increaser.value = 5
        self.language_mode.language_mode = None
        self.word_input.text = ""

    def __init__(self, **kwargs):
        super(AddFromDictionaryScreen, self).__init__(**kwargs)

        self.slider_tags = []

        self.selected_file = None  # path to currently selected file
