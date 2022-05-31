from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from ..flashcards.flashcard_database import FlashcardDataBase
from kivy.cache import Cache
from ..classes.slider_card import SliderCard
from kivy.clock import Clock
from ..classes.slider_tag import SliderTag
from ..classes.slider_box import SliderBox
from ..classes.utensils import UtensilDropUp, UtensilButton
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from ..classes.popups import display_card as display_s_card
from ..classes.popups import tags_popup, yes_no_popup, loading_popup
from ..classes.utils import a_difference_b
from kivy.app import App


class BackupContentScreen(Screen):
    cards_btn = ObjectProperty(None)
    boxes_btn = ObjectProperty(None)
    tags_btn = ObjectProperty(None)
    cards_slider = ObjectProperty(None)
    cards_container = ObjectProperty(None)
    tags_slider = ObjectProperty(None)
    tags_container = ObjectProperty(None)
    boxes_slider = ObjectProperty(None)
    boxes_container = ObjectProperty(None)
    box_cards_slider = ObjectProperty(None)
    box_cards_container = ObjectProperty(None)
    sliders_carousel = ObjectProperty(None)
    left_invisible = ObjectProperty(None)
    right_invisible = ObjectProperty(None)

    def discard(self):

        info_pop = yes_no_popup("are you sure?", self.width, 0.5,
                                lambda btn: App.get_running_app().switch_screen("database_settings_screen", "right"),
                                lambda btn: self.save())
        info_pop.open()

    def save(self):
        wheel = loading_popup("updating database...", self.width)
        wheel.open()

        Clock.schedule_once(lambda nt: self.insert_backup(), 0.05)
        Clock.schedule_once(lambda nt: wheel.dismiss(), 0.05)

    def insert_backup(self):

        database_f = Cache.get("app_info", "database_dir")
        aux_database_f = Cache.get("app_info", "aux_database_dir")
        original_boxes = FlashcardDataBase.retrieve_boxes(database_f)

        # ///// inserting boxes ////////////
        box_original_ids = {}   # hash map box_id in aux -> box_id in main database
        for s_box in self.slider_boxes:
            original = next((box for box in original_boxes if box.name == s_box.box.name), None)
            if original is not None:
                box_original_ids[s_box.box.id] = original.id
            else:
                key = s_box.box.id
                s_box.box.id = None
                FlashcardDataBase.insert_box(database_f, s_box.box)
                box_original_ids[key] = s_box.box.id
        # /////////////////////////////////

        # ///// inserting tags ////////////
        for s_tag in self.slider_tags:
            s_tag.tag.id = None
            FlashcardDataBase.insert_tag(database_f, s_tag.tag)
        # /////////////////////////////////

        # ///// inserting cards ////////////
        cards_original = {}  # hash map card_id in aux -> card_object in main
        aux_ids = [card.flashcard.id for card in self.slider_cards]
        for card in self.slider_cards:
            card.flashcard.id = None

        FlashcardDataBase.insert_cards(database_f, [card.flashcard for card in self.slider_cards])

        for aux_id, inserted_card in zip(aux_ids, [card.flashcard for card in self.slider_cards]):
            cards_original[aux_id] = inserted_card
        # ////////////////////////////////

        # ////// inserting box-cards relations /////
        for box_id, card_id, comp_nr in FlashcardDataBase.get_box_card_relations(aux_database_f):
            FlashcardDataBase.update_compartment(database_f, box_original_ids[box_id], [cards_original[card_id]], None)
            FlashcardDataBase.update_compartment(database_f, box_original_ids[box_id], [cards_original[card_id]], comp_nr - 1)
        # /////////////////////////////////////////

        App.get_running_app().switch_screen("database_settings_screen", "right")

    def on_slide_change(self, slide_index):

        self.cards_btn.state = "normal"
        self.tags_btn.state = "normal"
        self.boxes_btn.state = "normal"

        if slide_index == 0:
            self.cards_btn.state = "down"

            self.box_utensils.toggle(None, mode="close")
            self.box_cards_utensils.toggle(None, mode="close")
            self.tag_utensils.toggle(None, mode="close")
            self.refresh_card_utensils()

        elif slide_index == 1:
            self.tags_btn.state = "down"

            self.box_utensils.toggle(None, mode="close")
            self.box_cards_utensils.toggle(None, mode="close")
            self.card_utensils.toggle(None, mode="close")
            self.refresh_tag_utensils()

        else:
            self.boxes_btn.state = "down"

            self.card_utensils.toggle(None, mode="close")
            self.tag_utensils.toggle(None, mode="close")
            self.refresh_box_utensils()
            self.refresh_box_cards_utensils()

    def enable_disable_scroll(self, *args):
        if self.cards_container.height > self.cards_slider.height:
            self.cards_slider.do_scroll_y = True
        else:
            self.cards_slider.do_scroll_y = False

        if self.tags_container.height > self.tags_slider.height:
            self.tags_slider.do_scroll_y = True
        else:
            self.tags_slider.do_scroll_y = False

        if self.boxes_container.height > self.boxes_slider.height:
            self.boxes_slider.do_scroll_y = True
        else:
            self.boxes_slider.do_scroll_y = False

        if self.box_cards_container.height > self.box_cards_slider.height:
            self.box_cards_slider.do_scroll_y = True
        else:
            self.box_cards_slider.do_scroll_y = False

    def pull_cards(self, *args):
        marked = []
        for compartment in self.box_cards:
            marked += [card.flashcard for card in compartment if card.marked]

        marked_box = [box for box in self.slider_boxes if box.marked][0]

        database_f = Cache.get("app_info", "aux_database_dir")

        FlashcardDataBase.strip_box(database_f, marked_box.box.id, marked)

        to_remove = []
        for compartment in self.box_cards:
            to_remove += [card for card in compartment if card.marked]

        for card in to_remove:
            self.box_cards[card.flashcard.comp_nr - 1].remove(card)

        self.refresh_box_cards()
        self.box_cards_utensils.toggle(None, mode="close")

    def delete_cards(self, *args):
        marked = [card for card in self.slider_cards if card.marked]
        database_f = Cache.get("app_info", "aux_database_dir")

        FlashcardDataBase.delete_cards(database_f, [card.flashcard for card in marked])

        for card in marked:
            self.slider_cards.remove(card)

        # resetting boxes and box cards
        for box in self.slider_boxes:
            if box.marked:
                box.toggle_marked()

        self.box_cards.clear()
        self.refresh_box_cards()

        self.card_utensils.toggle(None, mode="close")
        self.refresh_all_cards()

    def show_tags_to_unlabel(self, *args):
        tags = []
        for card in self.slider_cards:
            tags += card.flashcard.tags

        tags = list(set(tags))  # getting a list of unique tag names

        database_f = Cache.get("app_info", "aux_database_dir")
        tags_pop = tags_popup("choose a tag to strip", self.size, database_f, self.unlabel_cards,
                              "there are no tags to choose", tags)

        tags_pop.open()

    def unlabel_cards(self, slider_tag):
        marked = [card for card in self.slider_cards if card.marked]

        for card in marked:
            if slider_tag.tag.name in card.flashcard.tags:
                card.flashcard.tags.remove(slider_tag.tag.name)
                card.refresh_info()
                card.adjust_style()
                card.draw()

        self.refresh_all_cards()

    def show_tags_to_label(self, *args):
        database_f = Cache.get("app_info", "aux_database_dir")
        tags_pop = tags_popup("choose tag to label cards", self.size, database_f, self.label_cards,
                              "there are no tags to choose")

        tags_pop.open()

    def label_cards(self, slider_tag):
        marked = [card for card in self.slider_cards if card.marked]

        for card in marked:
            if slider_tag.tag.name not in card.flashcard.tags:
                card.flashcard.tags.append(slider_tag.tag.name)
                card.refresh_info()
                card.adjust_style()
                card.draw()

        self.refresh_all_cards()

    def delete_box(self, *args):
        marked = [box for box in self.slider_boxes if box.marked][0]

        self.slider_boxes.remove(marked)

        self.box_utensils.toggle(None, mode="close")
        self.box_cards.clear()
        self.refresh_box_cards()
        self.refresh_all_boxes()

    def delete_tag(self, *args):

        marked = {tag.tag.name for tag in self.slider_tags if tag.marked}

        for card in self.slider_cards:
            if set(card.flashcard.tags).intersection(marked):
                card.flashcard.tags = a_difference_b(card.flashcard.tags, marked)
                card.refresh_info()
                card.adjust_style()
                card.draw()

        database_dir = Cache.get("app_info", "aux_database_dir")

        to_delete = [tag for tag in self.slider_tags if tag.marked]

        for tag in to_delete:
            self.slider_tags.remove(tag)
            FlashcardDataBase.delete_tag(database_dir, tag.tag)

        self.tag_utensils.toggle(None, mode="close")
        self.refresh_all_tags()

    def shift_card(self, utensil_btn):
        marked = []
        for compartment in self.box_cards:
            marked += [card for card in compartment if card.marked]
        marked = marked[0]

        chosen_box = [box for box in self.slider_boxes if box.marked][0]

        if utensil_btn == self.box_cards_utensils.items["up_btn"]:
            if marked.flashcard.comp_nr == 1:
                return

            self.box_cards[marked.flashcard.comp_nr - 1].remove(marked)
            marked.flashcard.comp_nr -= 1

        else:
            if marked.flashcard.comp_nr == chosen_box.box.nr_compartments:
                return

            self.box_cards[marked.flashcard.comp_nr - 1].remove(marked)
            marked.flashcard.comp_nr += 1

        database_f = Cache.get("app_info", "aux_database_dir")
        FlashcardDataBase.update_compartment(database_f, chosen_box.box.id, [marked.flashcard],
                                             marked.flashcard.comp_nr - 1)

        self.box_cards[marked.flashcard.comp_nr - 1].append(marked)

        self.box_cards_utensils.toggle(None, mode="close")
        self.refresh_box_cards()

    def choose_box(self, slider_box):
        marked = [box for box in self.slider_boxes if box.marked]
        aux_database_f = Cache.get("app_info", "aux_database_dir")

        if marked:
            marked = marked[0]
            if marked == slider_box:
                slider_box.toggle_marked()

            else:
                marked.toggle_marked()
                slider_box.toggle_marked()

        else:
            slider_box.toggle_marked()

        self.box_cards.clear()
        if marked != slider_box:  # whether user clicked new box or there was no marked boxes in slider

            for comp_nr in range(1, slider_box.box.nr_compartments + 1):
                retrieved_cards = FlashcardDataBase.retrieve_cards(aux_database_f, "box",
                                                                   box=slider_box.box.id, compartment=comp_nr)

                self.box_cards.append([])
                for flashcard in retrieved_cards:
                    flashcard.comp_nr = comp_nr
                    self.box_cards[comp_nr - 1].append(SliderCard(flashcard))

        self.refresh_box_cards()
        self.refresh_box_utensils()

    def refresh_tag_utensils(self, *args):
        marked = [tag for tag in self.slider_tags if tag.marked]

        if marked:
            self.tag_utensils.toggle(self.right_invisible, "up", mode="open")

        else:
            self.tag_utensils.toggle(None, mode="close")

    def refresh_box_cards_utensils(self, *args):
        marked = []
        for compartment in self.box_cards:
            marked += [card for card in compartment if card.marked]

        if not marked:
            self.box_cards_utensils.toggle(None, mode="close")

        elif len(marked) == 1:
            self.box_cards_utensils.items["up_btn"].bind(on_release=self.shift_card)
            self.box_cards_utensils.items["up_btn"].change_mode("enabled")
            self.box_cards_utensils.items["down_btn"].bind(on_release=self.shift_card)
            self.box_cards_utensils.items["down_btn"].change_mode("enabled")

            self.box_cards_utensils.toggle(self.right_invisible, "up", mode="open")

        else:
            self.box_cards_utensils.items["up_btn"].unbind(on_release=self.shift_card)
            self.box_cards_utensils.items["up_btn"].change_mode("disabled")
            self.box_cards_utensils.items["down_btn"].unbind(on_release=self.shift_card)
            self.box_cards_utensils.items["down_btn"].change_mode("disabled")

            self.box_cards_utensils.toggle(self.right_invisible, "up", mode="open")

    def refresh_card_utensils(self, *args):
        marked = [card for card in self.slider_cards if card.marked]

        if marked:
            self.card_utensils.toggle(self.right_invisible, "up", mode="open")

        else:
            self.card_utensils.toggle(None, mode="close")

    def refresh_box_utensils(self, *args):
        marked = [box for box in self.slider_boxes if box.marked]

        if marked:
            self.box_utensils.toggle(self.left_invisible, "up", mode="open")

        else:
            self.box_utensils.toggle(None, mode="close")

    def display_card(self, slider_card):
        display_s_card(slider_card, self.size)

    def refresh_box_cards(self):

        self.box_cards_container.clear_widgets()
        for comp_nr, compartment in enumerate(self.box_cards, 1):
            comp_lbl = Label(text=str(comp_nr), size_hint=(1, None), height=self.box_cards_container.width / 10,
                             color=get_color_from_hex("#444444"))
            self.box_cards_container.add_widget(comp_lbl)

            for card in compartment:
                if card.marked:
                    card.toggle_marked()

                card.bind(pos=card.draw, width=card.adjust_style)
                card.bind(size=self.box_cards_container.resize_v, on_hold=card.toggle_marked)
                card.bind(on_choose=self.display_card, marked=self.refresh_box_cards_utensils)
                self.box_cards_container.add_widget(card)

        self.box_cards_container.resize_v()
        self.box_cards_container.bind(height=self.enable_disable_scroll)

        self.box_cards_slider.scroll_y = 1

    def refresh_all_boxes(self):

        self.boxes_container.clear_widgets()
        for box in self.slider_boxes:
            box.bind(pos=box.draw, width=box.adjust_style)
            box.bind(size=box.draw, height=self.boxes_container.resize_v)
            box.bind(on_choose=self.choose_box)
            self.boxes_container.add_widget(box)

        if not self.slider_boxes:
            empty_lbl = Label(size_hint=(1, None), font_size=self.boxes_container.width / 7, height=self.boxes_slider.height,
                              halign="center", color=get_color_from_hex("#444444"), text="there are no boxes in the backup",
                              text_size=(self.boxes_slider.width, None))
            self.boxes_container.add_widget(empty_lbl)

        self.boxes_container.resize_v()

        self.boxes_container.bind(height=self.enable_disable_scroll)
        self.boxes_slider.scroll_y = 1

    def refresh_all_cards(self):

        self.cards_container.clear_widgets()
        for card in self.slider_cards:
            if card.marked:
                card.toggle_marked()

            self.cards_container.add_widget(card)
            card.bind(pos=card.draw, width=card.adjust_style)
            card.bind(size=self.cards_container.resize_v, on_choose=self.display_card)
            card.bind(on_hold=card.toggle_marked, marked=self.refresh_card_utensils)

        if not self.slider_cards:
            empty_lbl = Label(size_hint=(1, None), font_size=self.cards_container.width / 15, height=self.cards_slider.height,
                              halign="center", color=get_color_from_hex("#444444"), text="there are no cards in the backup",
                              text_size=(self.cards_slider.width, None))
            self.cards_container.add_widget(empty_lbl)

        self.cards_container.resize_v()

        self.cards_container.bind(height=self.enable_disable_scroll)
        self.cards_slider.scroll_y = 1

    def refresh_all_tags(self):

        self.tags_container.clear_widgets()
        for tag in self.slider_tags:
            self.tags_container.add_widget(tag)
            tag.bind(size=tag.draw, pos=self.tags_container.resize_v)
            tag.bind(pos=tag.adjust_style, on_choose=tag.toggle_marked, marked=self.refresh_tag_utensils)

        if not self.slider_tags:
            empty_lbl = Label(size_hint=(1, None), font_size=self.tags_container.width / 15, height=self.tags_slider.height,
                              halign="center", color=get_color_from_hex("#444444"), text="there are no tags in the backup",
                              text_size=(self.tags_slider.width, None))
            self.tags_container.add_widget(empty_lbl)

        self.tags_container.resize_v()

        self.tags_container.bind(height=self.enable_disable_scroll)
        self.tags_slider.scroll_y = 1

    def on_leave(self, *args):

        self.slider_boxes.clear()
        self.slider_cards.clear()
        self.slider_tags.clear()

        self.box_cards.clear()

        self.cards_container.clear_widgets()
        self.tags_container.clear_widgets()
        self.boxes_container.clear_widgets()

        self.box_cards_container.clear_widgets()

        aux_database_dir = Cache.get("app_info", "aux_database_dir")
        FlashcardDataBase.clear_database(aux_database_dir)

    def on_enter(self, *args):
        workdir = Cache.get("app_info", "work_dir") + "/data/textures"

        if self.card_utensils is None:
            self.card_utensils = UtensilDropUp(pos=(self.right_invisible.x, self.right_invisible.y))

            # preparing action buttons
            delete_btn = UtensilButton(workdir + "/delete_icon.png",
                                       height=self.right_invisible.width, width=self.right_invisible.width)
            unlabel_btn = UtensilButton(workdir + "/unlabel_icon.png",
                                        height=self.right_invisible.width, width=self.right_invisible.width)
            label_btn = UtensilButton(workdir + "/label_icon.png",
                                      height=self.right_invisible.width, width=self.right_invisible.width)

            delete_btn.bind(pos=delete_btn.draw, on_release=self.delete_cards)
            unlabel_btn.bind(pos=unlabel_btn.draw, on_release=self.show_tags_to_unlabel)
            label_btn.bind(pos=label_btn.draw, on_release=self.show_tags_to_label)

            self.card_utensils.items["delete_btn"] = delete_btn
            self.card_utensils.items["unlabel_btn"] = unlabel_btn
            self.card_utensils.items["label_btn"] = label_btn

            self.ids["additional_layout"].add_widget(self.card_utensils)

        if self.box_utensils is None:
            self.box_utensils = UtensilDropUp(pos=(self.left_invisible.x, self.left_invisible.y))

            # preparing action buttons
            delete_btn = UtensilButton(workdir + "/delete_icon.png",
                                       height=self.left_invisible.width, width=self.left_invisible.width)

            delete_btn.bind(pos=delete_btn.draw, on_release=self.delete_box)

            self.box_utensils.items["delete_btn"] = delete_btn

            self.ids["additional_layout"].add_widget(self.box_utensils)

        if self.box_cards_utensils is None:
            self.box_cards_utensils = UtensilDropUp(pos=(self.right_invisible.x, self.right_invisible.y))

            # preparing action buttons
            pull_btn = UtensilButton(workdir + "/pull_icon.png",
                                     height=self.right_invisible.width, width=self.right_invisible.width)
            down_btn = UtensilButton(workdir + "/down_icon.png",
                                     height=self.right_invisible.width, width=self.right_invisible.width)
            up_btn = UtensilButton(workdir + "/up_icon.png",
                                   height=self.right_invisible.width, width=self.right_invisible.width)

            pull_btn.bind(pos=pull_btn.draw, on_release=self.pull_cards)
            down_btn.bind(pos=down_btn.draw)
            up_btn.bind(pos=up_btn.draw)

            self.box_cards_utensils.items["up_btn"] = up_btn
            self.box_cards_utensils.items["pull_btn"] = pull_btn
            self.box_cards_utensils.items["down_btn"] = down_btn

            self.ids["additional_layout"].add_widget(self.box_cards_utensils)

        if self.tag_utensils is None:
            self.tag_utensils = UtensilDropUp(pos=(self.right_invisible.x, self.right_invisible.y))

            # preparing action buttons
            delete_btn = UtensilButton(workdir + "/delete_icon.png",
                                       height=self.right_invisible.width, width=self.right_invisible.width)

            delete_btn.bind(pos=delete_btn.draw, on_release=self.delete_tag)

            self.tag_utensils.items["delete_btn"] = delete_btn

            self.ids["additional_layout"].add_widget(self.tag_utensils)

    def on_pre_enter(self, *args):

        self.sliders_carousel.index = 0

        aux_database_f = Cache.get("app_info", "aux_database_dir")
        database_f = Cache.get("app_info", "database_dir")

        retrieved_cards = FlashcardDataBase.retrieve_cards(aux_database_f, "all")
        retrieved_tags = FlashcardDataBase.retrieve_tags(aux_database_f)
        retrieved_boxes = FlashcardDataBase.retrieve_boxes(aux_database_f)

        FlashcardDataBase.mark_redundant(database_f, retrieved_cards)
        FlashcardDataBase.mark_redundant_boxes(database_f, retrieved_boxes)

        for flashcard in retrieved_cards:
            self.slider_cards.append(SliderCard(flashcard))

        for tag in retrieved_tags:
            self.slider_tags.append(SliderTag(tag, 1))

        for box in retrieved_boxes:
            self.slider_boxes.append(SliderBox(box))

        Clock.schedule_once(lambda nt: self.refresh_all_cards(), 0.05)
        Clock.schedule_once(lambda nt: self.refresh_all_tags(), 0.05)
        Clock.schedule_once(lambda nt: self.refresh_all_boxes(), 0.05)

    def __init__(self, **kwargs):
        super(BackupContentScreen, self).__init__(**kwargs)

        self.slider_cards = []
        self.slider_tags = []
        self.slider_boxes = []
        self.box_cards = []

        self.card_utensils = None
        self.tag_utensils = None
        self.box_utensils = None
        self.box_cards_utensils = None
