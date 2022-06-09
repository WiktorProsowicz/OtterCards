from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.cache import Cache
from ..classes.slider_card import SliderCard
from ..classes.utensils import UtensilDropUp, UtensilButton
from kivy.metrics import dp
from kivy.app import App
from data.flashcards.flashcard_database import FlashcardDataBase, LengthError
from ..classes.popups import tags_popup, ok_popup, display_card as display_s_card


class CardWaitingRoomScreen(Screen):
    """
    Screen operates on auxiliary database to disjoin basic cards with those dynamically created. In Cache there are
    only ids of the handled cards, not the cards themselves because in every on_enter call list of displayed cards has to
    be updated in case one of them has been deleted, edited etc.
    """

    back_btn = ObjectProperty(None)
    cards_slider = ObjectProperty(None)
    cards_container = ObjectProperty(None)
    approve_btn = ObjectProperty(None)

    def proceed(self):

        database_f = Cache.get("app_info", "database_dir")

        flashcard_list = [card.flashcard for card in self.slider_cards]
        # setting ids to None so that they can be saved to main database
        for flashcard in flashcard_list:
            flashcard.id = None

        # get_from_file and get_from_dict tools make line length validation so new one is not necessary
        try:
            FlashcardDataBase.insert_cards(database_f, flashcard_list)

        except LengthError:
            warning_pop = ok_popup("some of the lines in cards are too long!", self.width, 0.3)
            warning_pop.open()

        else:
            aux_database_f = Cache.get("app_info", "aux_database_dir")
            FlashcardDataBase.clear_database(aux_database_f)
            App.get_running_app().switch_screen("add_cards_screen", "right")

    def discard(self):

        aux_database_f = Cache.get("app_info", "aux_database_dir")
        FlashcardDataBase.clear_database(aux_database_f)
        # FlashcardDataBase.delete_cards(aux_database_f, [card.flashcard for card in self.slider_cards])

        App.get_running_app().switch_screen("add_cards_screen", "right")

    def label_cards(self, slider_tag):
        aux_database_f = Cache.get("app_info", "aux_database_dir")

        to_insert = []
        for card in self.slider_cards:
            if card.marked and slider_tag.tag.name not in card.flashcard.tags:
                card.flashcard.tags.append(slider_tag.tag.name)
                card.refresh_info()
                to_insert.append(card)

        FlashcardDataBase.insert_cards(aux_database_f, [card.flashcard for card in to_insert])

        for card in to_insert:
            card.toggle_short_long()

        self.card_utensils.toggle(None, mode="close")
        self.refresh_cards()

    def show_tags(self, *args):

        database_dir = Cache.get("app_info", "database_dir")

        tags_pop = tags_popup("choose tag to label cards", self.size, database_dir, lambda obj: self.label_cards(obj),
                              "there are no tags to choose from", )
        tags_pop.open()

    """
    Method takes all marked cards and combines them into one by assigning all lines and unique tags into the first in order.
    """
    def merge_cards(self, *args):

        marked, marked_flashcards = [], []
        for card in self.slider_cards:
            if card.marked:
                marked.append(card)
                marked_flashcards.append(card.flashcard)

        for card in marked[1:]:
            self.slider_cards.remove(card)

        current_ids = Cache.get(self.name.replace("_screen", ""), "card_ids")
        for card in marked_flashcards[1:]:
            marked_flashcards[0].def_lines += card.def_lines
            marked_flashcards[0].hidden_lines += card.hidden_lines
            current_ids.remove(card.id)
        Cache.append(self.name.replace("_screen", ""), "card_ids", current_ids)

        aux_database_f = Cache.get("app_info", "aux_database_dir")
        database_f = Cache.get("app_info", "database_dir")

        FlashcardDataBase.insert_cards(aux_database_f, [marked_flashcards[0]])
        FlashcardDataBase.delete_cards(aux_database_f, marked_flashcards[1:])

        FlashcardDataBase.mark_redundant(database_f, [marked_flashcards[0]])
        marked[0].refresh_info()

        for card in self.slider_cards:
            if not card.shortened:
                card.toggle_short_long()

        marked[0].toggle_short_long()  # opening modified card
        self.card_utensils.toggle(None, mode="close")

        self.refresh_cards()

    def delete_cards(self, *args):

        aux_database_f = Cache.get("app_info", "aux_database_dir")
        to_delete = []
        current_ids = Cache.get(self.name.replace("_screen", ""), "card_ids")
        for card in self.slider_cards:
            if card.marked:
                to_delete.append(card)
                current_ids.remove(card.flashcard.id)

        Cache.append(self.name.replace("_screen", ""), "card_ids", current_ids)

        FlashcardDataBase.delete_cards(aux_database_f, [card.flashcard for card in to_delete])
        for card in to_delete:
            self.slider_cards.remove(card)

        self.card_utensils.toggle(None, mode="close")
        self.refresh_cards()

    def send_to_workshop(self, *args):
        Cache.append("card_workshop", "aux_mode", True)
        for card in self.slider_cards:
            if card.marked:
                Cache.append("card_workshop", "base_card", card.flashcard)
                break

        App.get_running_app().switch_screen("card_workshop_screen", "left")

    def refresh_card_utensils(self, *args):

        num_marked = 0
        for card in self.slider_cards:
            if card.marked:
                num_marked += 1

        if num_marked == 0:
            self.card_utensils.toggle(None, mode="close")

        elif num_marked == 1:
            self.card_utensils.toggle(self.approve_btn, "down", mode="open")

            self.card_utensils.items["delete_btn"].bind(on_release=self.delete_cards)
            self.card_utensils.items["delete_btn"].change_mode("enabled")

            self.card_utensils.items["edit_btn"].bind(on_release=self.send_to_workshop)
            self.card_utensils.items["edit_btn"].change_mode("enabled")

            self.card_utensils.items["label_btn"].bind(on_release=self.show_tags)
            self.card_utensils.items["label_btn"].change_mode("enabled")

            # you need several cards to merge
            self.card_utensils.items["merge_btn"].unbind(on_release=self.merge_cards)
            self.card_utensils.items["merge_btn"].change_mode("disabled")

        else:
            self.card_utensils.toggle(self.approve_btn, "down", mode="open")

            self.card_utensils.items["delete_btn"].bind(on_release=self.delete_cards)
            self.card_utensils.items["delete_btn"].change_mode("enabled")

            # you can't edit multiple cards
            self.card_utensils.items["edit_btn"].unbind(on_release=self.send_to_workshop)
            self.card_utensils.items["edit_btn"].change_mode("disabled")

            self.card_utensils.items["label_btn"].bind(on_release=self.show_tags)
            self.card_utensils.items["label_btn"].change_mode("enabled")

            self.card_utensils.items["merge_btn"].bind(on_release=self.merge_cards)
            self.card_utensils.items["merge_btn"].change_mode("enabled")

    def display_card(self, slider_card):
        display_s_card(slider_card, self.size)

    def refresh_cards(self):

        self.cards_container.clear_widgets()
        for card in self.slider_cards:
            self.cards_container.add_widget(card)
            card.bind(pos=card.draw, width=card.adjust_style)
            card.bind(size=self.cards_container.resize_v, on_choose=self.display_card)
            card.bind(on_hold=card.toggle_marked, marked=self.refresh_card_utensils)
            if card.marked:
                card.toggle_marked()

        self.cards_container.resize_v()

        if self.cards_container.height > self.cards_slider.height:
            self.cards_slider.do_scroll_y = True
        else:
            self.cards_slider.do_scroll_y = False

        self.cards_slider.scroll_y = 1

    def on_leave(self, *args):
        self.slider_cards.clear()
        self.cards_container.clear_widgets()
        self.card_utensils.toggle(None, mode="close")

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

    def on_pre_enter(self, *args):

        card_ids = Cache.get("card_waiting_room", "card_ids")
        aux_database_f = Cache.get("app_info", "aux_database_dir")
        database_f = Cache.get("app_info", "database_dir")

        retrieved_cards = FlashcardDataBase.retrieve_cards(aux_database_f, "id", ids=card_ids)
        FlashcardDataBase.mark_redundant(database_f, retrieved_cards)

        for card in retrieved_cards:
            self.slider_cards.append(SliderCard(card))

        self.refresh_cards()

    def __init__(self, **kwargs):
        super(CardWaitingRoomScreen, self).__init__(**kwargs)

        self.card_utensils = None

        self.slider_cards = []