from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.cache import Cache
from data.flashcards.flashcard_database import FlashcardDataBase
from data.classes.slider_card import SliderCard
from ..classes.utensils import UtensilButton, UtensilDropUp
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.label import Label
from kivy.app import App
from ..classes.clickable_label import ClickableLabel
from ..classes.popups import display_card as display_s_card, tags_popup
from kivy.clock import Clock


class CardsCollectionScreen(Screen):
    title_label = ObjectProperty(None)
    slider_cards = ListProperty([])
    slider_container = ObjectProperty(None)
    slider = ObjectProperty(None)
    more_btn = ObjectProperty(None)
    main_layout = ObjectProperty(None)

    def send_to_workshop(self, slider_card):
        Cache.append("card_workshop", "base_card", slider_card.flashcard)
        Cache.append("card_workshop", "aux_mode", False)
        App.get_running_app().switch_screen("card_workshop_screen", "up")

    def label_cards(self, slider_tag):

        database_f = Cache.get("app_info", "database_dir")
        for card in self.to_label:
            if slider_tag.tag.name not in card.flashcard.tags:
                card.flashcard.tags.append(slider_tag.tag.name)
                FlashcardDataBase.insert_cards(database_f, [card.flashcard])

                old_index = self.slider_cards.index(card)
                self.slider_cards.remove(card)
                self.slider_cards.insert(old_index, SliderCard(card.flashcard))    # replacing old card with new one that has proper tags label

        self.toggle_label_mode(None)
        self.refresh()
        self.utensils.toggle(self.more_btn, mode="open")

    def show_tags(self, title_lbl):

        self.to_label.clear()
        for card in self.slider_cards:
            if card.to_label:
                self.to_label.append(card)

        if not self.to_label:
            return False

        database_dir = Cache.get("app_info", "database_dir")
        tags_pop = tags_popup("choose tag to label cards", self.size, database_dir, lambda tag: self.label_cards(tag))

        tags_pop.open()

    def toggle_label_mode(self, label_btn):

        self.label_mode = not self.label_mode

        if self.label_mode:

            if self.edit_mode:
                self.toggle_edit_mode(None)

            if self.delete_mode:
                self.toggle_delete_mode(None)

            self.utensils.toggle(None, mode="close")

            self.utensils.items["label_btn"].change_mode("chosen")

            self.title_label.text = "click to label"
            self.title_label.bind(on_release=self.show_tags)
            self.title_label.toggle_mode("labelling")

        else:

            self.utensils.items["label_btn"].change_mode("enabled")

            main_filter = Cache.get("cards_collection", "main_filter")
            self.title_label.text = "all cards" if main_filter == "all" else main_filter
            self.title_label.unbind(on_release=self.show_tags)
            self.title_label.toggle_mode("normal")

        for card in self.slider_cards:

            # if not card.shortened:
            #     card.toggle_short_long(None)

            card.to_label = True
            card.toggle_label(None)  # this will show card in not-to-label mode

            if self.label_mode:
                # card.unbind(on_choose=card.toggle_short_long)
                card.unbind(on_choose=self.display_card)
                card.bind(on_choose=card.toggle_label)

            else:
                card.opacity = 1

                # card.bind(on_choose=card.toggle_short_long)
                card.bind(on_choose=self.display_card)
                card.unbind(on_choose=card.toggle_label)

    def toggle_edit_mode(self, edit_btn):

        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            if self.delete_mode:
                self.toggle_delete_mode(None)

            if self.label_mode:
                self.toggle_label_mode(None)

            self.utensils.toggle(None, mode="close")

            self.title_label.text = "choose to edit"

            self.utensils.items["edit_btn"].change_mode("chosen")

        else:
            main_filter = Cache.get("cards_collection", "main_filter")
            self.title_label.text = "all cards" if main_filter == "all" else main_filter

            self.utensils.items["edit_btn"].change_mode("enabled")

            if not self.utensils.open:
                self.utensils.toggle(self.more_btn)

        for card in self.slider_cards:
            # if not card.shortened:
            #     card.toggle_short_long(None)

            if self.edit_mode:
                card.bind(on_choose=self.send_to_workshop)
                card.unbind(on_choose=self.display_card)
            else:
                card.unbind(on_choose=self.send_to_workshop)
                card.bind(on_choose=self.display_card)

    def delete_cards(self, title_lbl):
        database_f = Cache.get("app_info", "database_dir")
        main_filter = Cache.get("cards_collection", "main_filter")
        to_remove, flashcards_to_remove = [], []
        for card in self.slider_cards:
            if card.to_delete:
                flashcards_to_remove.append(card.flashcard)
                to_remove.append(card)

        if not to_remove:
            return False    # if there are no cards to delete, delete_mode shouldn't be completed

        if main_filter == "all":
            FlashcardDataBase.delete_cards(database_f, flashcards_to_remove)
        else:
            FlashcardDataBase.strip_tags(database_f, main_filter, flashcards_to_remove)

        for card in to_remove:
            self.slider_cards.remove(card)

        self.toggle_delete_mode(None)
        self.refresh()
        self.utensils.toggle(self.more_btn, mode="open")

    def toggle_delete_mode(self, delete_btn):

        self.delete_mode = not self.delete_mode

        if self.delete_mode:
            if self.edit_mode:
                self.toggle_edit_mode(None)

            if self.label_mode:
                self.toggle_label_mode(None)

            self.utensils.toggle(None, mode="close")

            self.title_label.text = "click to delete"
            self.title_label.bind(on_release=self.delete_cards)
            self.title_label.toggle_mode("deleting")

            self.utensils.items["delete_btn"].change_mode("chosen")

        else:
            main_filter = Cache.get("cards_collection", "main_filter")
            self.title_label.text = "all cards" if main_filter == "all" else main_filter
            self.title_label.unbind(on_release=self.delete_cards)
            self.title_label.toggle_mode("normal")

            self.utensils.items["delete_btn"].change_mode("enabled")

            if not self.utensils.open:
                self.utensils.toggle(self.more_btn)

        for card in self.slider_cards:
            # if not card.shortened:
            #     card.toggle_short_long(None)

            # preparing all cards style
            card.to_delete = True
            card.toggle_delete(None)  # this will show the card in not-to-delete style

            if self.delete_mode:
                card.bind(on_choose=card.toggle_delete)
                # card.unbind(on_choose=card.toggle_short_long)
                card.unbind(on_choose=self.display_card)

            else:
                # restoring card info and style
                card.opacity = 1

                card.unbind(on_choose=card.toggle_delete)
                # card.bind(on_choose=card.toggle_short_long)
                card.bind(on_choose=self.display_card)

    def on_leave(self, *args):
        self.slider_container.clear_widgets()
        self.slider_cards.clear()

        if self.delete_mode:
            self.toggle_delete_mode(None)

        if self.edit_mode:
            self.toggle_edit_mode(None)

        if self.label_mode:
            self.toggle_label_mode(None)

        self.utensils.toggle(None, mode="close")

        if self.so_empty_lbl in self.main_layout.children:
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
            label_btn = UtensilButton(work_dir + "/label_icon.png", work_dir + "/label_icon_chosen.png",
                                      height=self.more_btn.height, width=self.more_btn.width)

            delete_btn.bind(pos=delete_btn.draw)
            edit_btn.bind(pos=edit_btn.draw)
            add_btn.bind(pos=add_btn.draw,
                         on_release=lambda btn: App.get_running_app().switch_screen("add_cards_screen", "left"))
            label_btn.bind(pos=label_btn.draw)

            self.utensils.items["delete_btn"] = delete_btn
            self.utensils.items["edit_btn"] = edit_btn
            self.utensils.items["add_btn"] = add_btn
            self.utensils.items["label_btn"] = label_btn

            self.more_btn.bind(on_release=self.utensils.toggle)
            self.ids["additional_layout"].add_widget(self.utensils)

        self.empty_info()
        self.update_buttons()

    def on_pre_enter(self, *args):
        main_filter = Cache.get("cards_collection", "main_filter")
        database_f = Cache.get("app_info", "database_dir")

        if main_filter == "all":
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "all", limit=50)
            self.title_label.text = "all cards"
        else:
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "tag", tag=main_filter, limit=50)
            self.title_label.text = main_filter

        retrieved_cards.sort(key=lambda flashcard: (flashcard.last_update, flashcard.id), reverse=True)
        self.loaded_entire_collection = True if len(retrieved_cards) < 50 else False

        for card in retrieved_cards:
            self.slider_cards.append(SliderCard(card))

        Clock.schedule_once(lambda nt: self.refresh(), 0.07)
        self.slider.scroll_y = 1

    # for async loading card widgets
    def load_cards(self, *args):

        not_ids = [s_card.flashcard.id for s_card in self.slider_cards]
        database_f = Cache.get("app_info", "database_dir")
        main_filter = Cache.get("cards_collection", "main_filter")

        if main_filter == "all":
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "all", limit=50, not_ids=not_ids)
        else:
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "tag", tag=main_filter, limit=50, not_ids=not_ids)

        previous_len = len(self.slider_cards)
        if previous_len == 0:
            self.loaded_entire_collection = True

        for card in retrieved_cards:
            s_card = SliderCard(card)
            self.slider_cards.append(s_card)

        self.refresh()
        self.slider.scroll_y = 1 - (previous_len / (previous_len + len(retrieved_cards)))

    def display_card(self, slider_card):
        display_s_card(slider_card, self.size)

    # method used to load all possessed cards to the slider container
    def refresh(self):
        self.slider_container.clear_widgets()
        for card in self.slider_cards:
            self.slider_container.add_widget(card)
            card.bind(pos=card.draw, width=card.adjust_style)
            # card.bind(size=self.slider_container.resize_v, on_choose=card.toggle_short_long)
            card.bind(size=self.slider_container.resize_v, on_choose=self.display_card)

        if not self.loaded_entire_collection:
            load_lbl = ClickableLabel(size_hint=(1, None), height=self.title_label.font_size * 0.8,
                                      color=get_color_from_hex("#444444"), font_size=self.title_label.font_size * 0.6,
                                      halign="center", text="load more")
            load_lbl.bind(on_release=self.load_cards)
            self.slider_container.add_widget(load_lbl)

        self.slider_container.resize_v()

        # if self.slider_container.height > self.slider.height:
        #     self.slider.do_scroll_y = True
        # else:
        #     self.slider.do_scroll_y = False

        self.slider.do_scroll_y = True

        if self.utensils is not None:
            self.update_buttons()

    def update_buttons(self):
        # buttons actions and appearance based on number of cards
        if self.slider_cards:
            self.utensils.items["delete_btn"].bind(on_release=self.toggle_delete_mode)
            self.utensils.items["delete_btn"].change_mode("enabled")
            self.utensils.items["edit_btn"].bind(on_release=self.toggle_edit_mode)
            self.utensils.items["edit_btn"].change_mode("enabled")
            self.utensils.items["label_btn"].bind(on_release=self.toggle_label_mode)
            self.utensils.items["label_btn"].change_mode("enabled")

        else:
            self.utensils.items["delete_btn"].unbind(on_release=self.toggle_delete_mode)
            self.utensils.items["delete_btn"].change_mode("disabled")
            self.utensils.items["edit_btn"].unbind(on_release=self.toggle_edit_mode)
            self.utensils.items["edit_btn"].change_mode("disabled")
            self.utensils.items["label_btn"].unbind(on_release=self.toggle_label_mode)
            self.utensils.items["label_btn"].change_mode("disabled")

    def empty_info(self):
        # adding encouraging label in case there are no tags
        if not self.slider_cards:

            if self.slider_cards and self.so_empty_lbl in self.main_layout.children:
                self.main_layout.remove_widget(self.so_empty_lbl)

            if Cache.get("cards_collection", "main_filter") == "all":
                text = "so empty...\nconsider adding some cards!"
            else:
                text = "so empty...\nconsider labelling some cards\nwith this tag!"

            self.so_empty_lbl = Label(text=text, size_hint=(1, None),
                                      pos_hint={"center_y": 0.7, "center_x": 0.5},
                                      color=get_color_from_hex("#AAAAAA"), font_size=self.slider_container.width * 0.07)

            self.main_layout.add_widget(self.so_empty_lbl)

        elif self.slider_cards and self.so_empty_lbl in self.main_layout.children:
            self.main_layout.remove_widget(self.so_empty_lbl)

    def __init__(self, **kwargs):
        super(CardsCollectionScreen, self).__init__(**kwargs)

        self.utensils = None

        self.delete_mode = False
        self.edit_mode = False
        self.label_mode = False

        self.so_empty_lbl = None

        self.to_label = []  # list of slider_cards that are chosen to be labeled in show_tags function

        self.loaded_entire_collection = False   # bool var saying whether there should be loaded a label "load more"
