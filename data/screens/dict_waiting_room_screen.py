from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.cache import Cache
from ..classes.utensils import UtensilButton, UtensilDropUp
from kivy.metrics import dp
from data.flashcards.flashcard_database import FlashcardDataBase
from ..classes.slider_card import SliderCard
from ..classes.smart_input import SmartInput
from .card_waiting_room_screen import CardWaitingRoomScreen
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from ..data_processing import get_cards_from_dictionary


class DictWaitingRoomScreen(Screen):
    main_layout = ObjectProperty(None)
    title_label = ObjectProperty(None)
    cards_slider = ObjectProperty(None)
    extras_slider = ObjectProperty(None)
    exceptions_slider = ObjectProperty(None)
    approve_btn = ObjectProperty(None)
    back_btn = ObjectProperty(None)

    cards_container = ObjectProperty(None)
    extras_container = ObjectProperty(None)
    exceptions_container = ObjectProperty(None)

    pages = ObjectProperty(None)

    def proceed(self):
        CardWaitingRoomScreen.proceed(self)

    def discard(self):
        CardWaitingRoomScreen.discard(self)

    def delete_words(self, *args):
        if self.pages.page == 0:
            to_delete = [exception for exception in self.slider_exceptions if exception.marked]
            current_words = Cache.get("dict_waiting_room", "exceptions")
        else:
            to_delete = [extra for extra in self.slider_extras if extra.marked]
            current_words = Cache.get("dict_waiting_room", "extras")

        for text in [word.text for word in to_delete]:
            current_words.remove(text)

        if self.pages.page == 0:
            Cache.append("dict_waiting_room", "exceptions", current_words)
        else:
            Cache.append("dict_waiting_room", "extras", current_words)

        for slider_word in to_delete:
            if self.pages.page == 0:
                self.slider_exceptions.remove(slider_word)
            else:
                self.slider_extras.remove(slider_word)

        self.word_utensils.toggle(None, mode="close")
        if self.pages.page == 0:
            self.refresh_exceptions()
        else:
            self.refresh_extras()

    def edit_word(self, *args):
        if self.pages.page == 0:
            for exception in self.slider_exceptions:
                if exception.marked:
                    word_to_edit = exception
                    break
        else:
            for extra in self.slider_extras:
                if extra.marked:
                    word_to_edit = extra
                    break

        word_to_edit.disabled = False
        word_to_edit.focus = True
        old_text = word_to_edit.text

        if self.pages.page == 0:
            current_words = Cache.get("dict_waiting_room", "exceptions")
            current_words.remove(old_text)
            Cache.append("dict_waiting_room", "exceptions", current_words)
        else:
            current_words = Cache.get("dict_waiting_room", "extras")
            current_words.remove(old_text)
            Cache.append("dict_waiting_room", "extras", current_words)

        # this will trigger the function when the word will be unfocused
        word_to_edit.bind(focus=self.save_word)

    def save_word(self, word, focus):
        # strip all focus observers
        word.unbind(focus=self.save_word)
        word.disabled = True

        if self.pages.page == 0:
            current_words = Cache.get("dict_waiting_room", "exceptions")
            current_words.append(word.text)
            Cache.append("dict_waiting_room", "exceptions", current_words)
        else:
            current_words = Cache.get("dict_waiting_room", "extras")
            current_words.append(word.text)
            Cache.append("dict_waiting_room", "extras", current_words)

        self.word_utensils.toggle(None, mode="close")
        word.toggle_marked()    # unmarking the word

    def search_words(self, *args):
        if self.pages.page == 0:
            to_search = [exception.text for exception in self.slider_exceptions if exception.marked]
        else:
            to_search = [extra.text for extra in self.slider_extras if extra.marked]

        self.delete_words()     # this will delete searched words because they are marked

        workdir = Cache.get("app_info", "work_dir")
        wheel = Image(source=workdir + "/data/textures/loading_screen.png",
                      allow_stretch=True, pos_hint={"center_x": 0.5, "center_y": 0.5})

        loading_pop = Popup(title="collecting cards...", auto_dismiss=False,
                            size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 1),
                            title_color=get_color_from_hex("#444444"),
                            background=workdir + "/data/textures/popup_background.png",
                            title_size=self.title_label.font_size * 0.7, height=self.width * 0.9 / 2,
                            content=wheel, border=[0, 0, 0, 0])
        loading_pop.open()
        Clock.schedule_once(lambda nt: self.pre_save_cards(to_search), .2)
        Clock.schedule_once(lambda nt: loading_pop.dismiss(), .2)

    def pre_save_cards(self, words):
        language_mode = Cache.get("dict_waiting_room", "language_mode")
        subdefs_limit = Cache.get("dict_waiting_room", "subdefs_limit")
        cards_limit = Cache.get("dict_waiting_room", "cards_limit")
        get_hinted = Cache.get("dict_waiting_room", "get_hinted")

        retrieved_cards, extras, exceptions = get_cards_from_dictionary("", language_mode, subdefs_limit, cards_limit,
                                                                        get_hinted, words=words)

        aux_database_f = Cache.get("app_info", "aux_database_dir")
        FlashcardDataBase.insert_cards(aux_database_f, retrieved_cards)

        current_ids = Cache.get("dict_waiting_room", "card_ids")
        for card in retrieved_cards:
            current_ids.append(card.id)
        Cache.append("dict_waiting_room", "card_ids", current_ids)

        current_exceptions = Cache.get("dict_waiting_room", "exceptions")
        for exception in exceptions:
            current_exceptions.append(exception)
        Cache.append("dict_waiting_room", "exceptions", current_exceptions)

        current_extras = Cache.get("dict_waiting_room", "extras")
        for extra in extras:
            current_extras.append(extra)
        Cache.append("dict_waiting_room", "extras", current_extras)

        self.update_slider_lists()

        self.refresh_cards()
        self.refresh_extras()
        self.refresh_exceptions()

    def refresh_word_utensils(self, *args):
        num_marked = 0
        if self.pages.page == 0:
            for exception in self.slider_exceptions:
                if exception.marked:
                    num_marked += 1
        else:
            for extra in self.slider_extras:
                if extra.marked:
                    num_marked += 1

        if num_marked == 0:
            self.word_utensils.toggle(None, mode="close")

        elif num_marked == 1:
            self.word_utensils.toggle(self.approve_btn, "down", mode="open")

            self.word_utensils.items["delete_btn"].bind(on_release=self.delete_words)
            self.word_utensils.items["delete_btn"].change_mode("enabled")

            self.word_utensils.items["edit_btn"].bind(on_release=self.edit_word)
            self.word_utensils.items["edit_btn"].change_mode("enabled")

            self.word_utensils.items["search_btn"].bind(on_release=self.search_words)
            self.word_utensils.items["search_btn"].change_mode("enabled")

        else:
            self.word_utensils.toggle(self.approve_btn, "down", mode="open")

            self.word_utensils.items["delete_btn"].bind(on_release=self.delete_words)
            self.word_utensils.items["delete_btn"].change_mode("enabled")

            # you can't edit several words at once
            self.word_utensils.items["edit_btn"].unbind(on_release=self.edit_word)
            self.word_utensils.items["edit_btn"].change_mode("disabled")

            self.word_utensils.items["search_btn"].bind(on_release=self.search_words)
            self.word_utensils.items["search_btn"].change_mode("enabled")

    def hide_utensils(self):

        if self.pages.page == 0:
            self.card_utensils.toggle(None, mode="close")

            self.refresh_word_utensils()

        elif self.pages.page == 1:
            self.card_utensils.toggle(None, mode="close")

            self.refresh_word_utensils()

        else:
            self.word_utensils.toggle(None, mode="close")

            self.refresh_card_utensils()

    def refresh_exceptions(self):
        self.exceptions_container.clear_widgets()
        for exception in self.slider_exceptions:
            self.exceptions_container.add_widget(exception)
            exception.bind(pos=self.exceptions_container.resize_v, text=exception.resize)
            exception.bind(line_height=exception.resize, on_hold=exception.toggle_marked, marked=self.refresh_word_utensils)
            exception.disabled = True
            exception.to_edit = False

            if exception.marked:
                exception.toggle_marked()

        self.exceptions_container.bind(height=self.enable_disable_exceptions_scroll)
        self.exceptions_container.resize_v()

        self.exceptions_slider.scroll_y = 1

    def refresh_extras(self):
        self.extras_container.clear_widgets()
        for extra in self.slider_extras:
            self.extras_container.add_widget(extra)
            extra.bind(pos=self.extras_container.resize_v, text=extra.resize)
            extra.bind(line_height=extra.resize, on_hold=extra.toggle_marked, marked=self.refresh_word_utensils)
            extra.disabled = True
            extra.to_edit = False

            if extra.marked:
                extra.toggle_marked()

        self.extras_container.bind(height=self.enable_disable_extras_scroll)
        self.extras_container.resize_v()
        self.enable_disable_extras_scroll()
        self.extras_slider.scroll_y = 1

    def enable_disable_extras_scroll(self, *args):
        if self.extras_container.height > self.extras_slider.height:
            self.extras_slider.do_scroll_y = True
        else:
            self.extras_slider.do_scroll_y = False

    def enable_disable_exceptions_scroll(self, *args):
        if self.exceptions_container.height > self.exceptions_slider.height:
            self.exceptions_slider.do_scroll_y = True
        else:
            self.exceptions_slider.do_scroll_y = False

    def label_cards(self, slider_tag):
        CardWaitingRoomScreen.label_cards(self, slider_tag)

    def show_tags(self, *args):
        CardWaitingRoomScreen.show_tags(self)

    def merge_cards(self, *args):
        CardWaitingRoomScreen.merge_cards(self)

    def delete_cards(self, *args):
        CardWaitingRoomScreen.delete_cards(self)

    def send_to_workshop(self, *args):
        CardWaitingRoomScreen.send_to_workshop(self)

    def refresh_card_utensils(self, *args):
        CardWaitingRoomScreen.refresh_card_utensils(self)

    def refresh_cards(self):
        CardWaitingRoomScreen.refresh_cards(self)

    def on_leave(self, *args):
        self.slider_cards.clear()
        self.slider_exceptions.clear()
        self.slider_extras.clear()

        self.cards_container.clear_widgets()
        self.extras_container.clear_widgets()
        self.exceptions_container.clear_widgets()

        self.card_utensils.toggle(None, mode="close")
        self.word_utensils.toggle(None, mode="close")

    def on_enter(self, *args):
        # initializing utensils (in on_enter because otherwise utensils might have wrong size)
        if self.card_utensils is None:
            self.card_utensils = UtensilDropUp(pos=(self.approve_btn.x, -dp(10)))

            # preparing action buttons
            work_dir = Cache.get("app_info", "work_dir") + "/data/textures"
            delete_btn = UtensilButton(work_dir + "/delete_icon.png", work_dir + "/delete_icon_chosen.png",
                                       height=self.approve_btn.height, width=self.approve_btn.width)
            edit_btn = UtensilButton(work_dir + "/edit_icon.png", work_dir + "/edit_icon_chosen.png",
                                     height=self.approve_btn.height, width=self.approve_btn.width)
            label_btn = UtensilButton(work_dir + "/label_icon.png", work_dir + "/label_icon_chosen.png",
                                      height=self.approve_btn.height, width=self.approve_btn.width)
            merge_btn = UtensilButton(work_dir + "/merge_icon.png",
                                      height=self.approve_btn.height, width=self.approve_btn.width)

            delete_btn.bind(pos=delete_btn.draw)
            edit_btn.bind(pos=edit_btn.draw)
            label_btn.bind(pos=label_btn.draw)
            merge_btn.bind(pos=merge_btn.draw)

            self.card_utensils.items["delete_btn"] = delete_btn
            self.card_utensils.items["edit_btn"] = edit_btn
            self.card_utensils.items["label_btn"] = label_btn
            self.card_utensils.items["merge_btn"] = merge_btn

            self.ids["additional_layout"].add_widget(self.card_utensils)

        if self.word_utensils is None:
            self.word_utensils = UtensilDropUp(pos=(self.approve_btn.x, -dp(10)))

            # preparing action buttons
            work_dir = Cache.get("app_info", "work_dir") + "/data/textures"
            delete_btn = UtensilButton(work_dir + "/delete_icon.png",
                                       height=self.approve_btn.height, width=self.approve_btn.width)
            edit_btn = UtensilButton(work_dir + "/edit_icon.png",
                                     height=self.approve_btn.height, width=self.approve_btn.width)
            search_btn = UtensilButton(work_dir + "/search_icon.png",
                                       height=self.approve_btn.height, width=self.approve_btn.width)

            delete_btn.bind(pos=delete_btn.draw)
            edit_btn.bind(pos=edit_btn.draw)
            search_btn.bind(pos=search_btn.draw)

            self.word_utensils.items["delete_btn"] = delete_btn
            self.word_utensils.items["edit_btn"] = edit_btn
            self.word_utensils.items["search_btn"] = search_btn

            self.ids["additional_layout"].add_widget(self.word_utensils)

        self.pages.page = 2

    def update_slider_lists(self):
        aux_database_f = Cache.get("app_info", "aux_database_dir")
        database_f = Cache.get("app_info", "database_dir")

        card_ids = Cache.get("dict_waiting_room", "card_ids")
        extras = Cache.get("dict_waiting_room", "extras")
        exceptions = Cache.get("dict_waiting_room", "exceptions")

        retrieved_cards = FlashcardDataBase.retrieve_cards(aux_database_f, "id", ids=card_ids)
        FlashcardDataBase.mark_redundant(database_f, retrieved_cards)

        self.slider_cards.clear()
        self.slider_exceptions.clear()
        self.slider_extras.clear()

        for card in retrieved_cards:
            self.slider_cards.append(SliderCard(card))

        workdir = Cache.get("app_info", "work_dir")
        for extra in extras:
            slider_extra = SmartInput(workdir + "/data/textures/line_input_marked.png", text=extra, size_hint=(1, None),
                                      font_size=1,
                                      height=1, do_wrap=True, multiline=True, halign="left",
                                      valign="middle", padding=(self.extras_container.width / 15, dp(6)),
                                      foreground_color=get_color_from_hex("#444444"),
                                      background_normal=workdir + f"/data/textures/def_line_input_normal.png",
                                      background_active=workdir + "/data/textures/line_input_focused.png")
            self.slider_extras.append(slider_extra)

        for exception in exceptions:
            slider_exception = SmartInput(workdir + "/data/textures/line_input_marked.png", text=exception,
                                          size_hint=(1, None),
                                          font_size=1,
                                          height=1, do_wrap=True, multiline=True, halign="left",
                                          valign="middle", padding=(self.extras_container.width / 15, dp(6)),
                                          foreground_color=get_color_from_hex("#444444"),
                                          background_normal=workdir + f"/data/textures/def_line_input_normal.png",
                                          background_active=workdir + "/data/textures/line_input_focused.png")
            self.slider_exceptions.append(slider_exception)

    def on_pre_enter(self, *args):

        self.update_slider_lists()

        self.refresh_cards()
        self.refresh_extras()
        self.refresh_exceptions()

    def __init__(self, **kwargs):
        super(DictWaitingRoomScreen, self).__init__(**kwargs)

        self.card_utensils = None
        self.word_utensils = None

        self.slider_cards = []
        self.slider_extras = []
        self.slider_exceptions = []

