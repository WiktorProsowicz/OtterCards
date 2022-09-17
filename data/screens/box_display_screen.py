from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.cache import Cache
from datetime import datetime
from kivy.clock import Clock
from ..flashcards.flashcard_database import FlashcardDataBase, Tag
from ..classes.slider_tag import SliderTag
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.animation import Animation
from ..classes.horizontal_slider_tag import HorizontalSliderTag
from ..classes.slider_card import SliderCard
from kivy.uix.label import Label
from ..classes.utensils import UtensilDropUp, UtensilButton
from ..classes.popups import display_card as display_s_card


class BoxDisplayScreen(Screen):
    base_box_widget = ObjectProperty(None)
    created_lbl = ObjectProperty(None)
    cards_number_lbl = ObjectProperty(None)
    cards_left_lbl = ObjectProperty(None)
    tags_dropdown = ObjectProperty(None)
    left_slider = ObjectProperty(None)
    right_slider = ObjectProperty(None)
    tags_slider = ObjectProperty(None)
    pages = ObjectProperty(None)
    tags_container = ObjectProperty(None)
    left_container = ObjectProperty(None)
    right_container = ObjectProperty(None)
    back_btn = ObjectProperty(None)
    right_invisible = ObjectProperty(None)
    left_invisible = ObjectProperty(None)

    def select_tag(self, item, tag):

        # if self.tags_container.children and tag.name == self.tags_container.children[0].tag.name:
        #     return

        self.tags_container.clear_widgets()

        h_slider_tag = HorizontalSliderTag(tag)
        h_slider_tag.bind(pos=lambda obj, pos: obj.adjust_style(), height=lambda obj, h: obj.adjust_style())
        h_slider_tag.bind(size=lambda obj, size: obj.draw(), width=self.tags_container.resize_h)

        self.tags_container.add_widget(h_slider_tag)

        self.tags_container.bind(width=self.enable_disable_scroll)
        self.tags_slider.scroll_x = 0

        self.right_utensils.toggle(None, mode="close")

        # filling up right container
        database_f = Cache.get("app_info", "database_dir")

        not_ids = []
        for compartment in self.l_slider_cards:
            not_ids += [card.flashcard.id for card in compartment]

        if tag.name == "all cards":
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "all", not_ids=not_ids)
        else:
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "tag", tag=tag.name, not_ids=not_ids)

        self.r_slider_cards.clear()
        for card in retrieved_cards:
            self.r_slider_cards.append(SliderCard(card))

        self.refresh_right()

    def enable_disable_scroll(self, *args):
        if self.tags_container.width > self.tags_slider.width:
            self.tags_slider.do_scroll_x = True
        else:
            self.tags_slider.do_scroll_x = False

        if self.right_container.width > self.right_slider.width:
            self.right_slider.do_scroll_x = True
        else:
            self.right_slider.do_scroll_x = False

        if self.left_container.width > self.left_slider.width:
            self.left_slider.do_scroll_x = True
        else:
            self.left_slider.do_scroll_x = False

    def enhance_dropdown(self, *args):

        with self.tags_dropdown.container.canvas.before:
            Color(rgb=get_color_from_hex("#FFFFFF"), a=.7)
            Rectangle(size=self.tags_dropdown.container.size, pos=self.tags_dropdown.container.pos)

        self.tags_dropdown.opacity = 0
        anim = Animation(opacity=1, duration=.2)
        anim.start(self.tags_dropdown)

    def update_labels(self, *args):

        self.cards_number_lbl.text = f"cards being learned: \n{self.base_box_widget.box.nr_cards}"
        self.cards_left_lbl.text = "cards {adj}:\n{nr}".format(
            adj="revised" if self.base_box_widget.box.is_special else "learned", nr=self.base_box_widget.box.cards_left)

    def shift_card(self, utensil_btn):
        marked = []
        for compartment in self.l_slider_cards:
            marked += [card for card in compartment if card.marked]
        marked = marked[0]

        if utensil_btn == self.left_utensils.items["up_btn"]:
            if marked.flashcard.comp_nr == 1:
                return

            self.l_slider_cards[marked.flashcard.comp_nr - 1].remove(marked)
            marked.flashcard.comp_nr -= 1

        else:
            if marked.flashcard.comp_nr == self.base_box_widget.box.nr_compartments:
                return

            self.l_slider_cards[marked.flashcard.comp_nr - 1].remove(marked)
            marked.flashcard.comp_nr += 1

        database_f = Cache.get("app_info", "database_dir")
        FlashcardDataBase.update_compartment(database_f, self.base_box_widget.box.id, [marked.flashcard],
                                             marked.flashcard.comp_nr - 1)

        self.l_slider_cards[marked.flashcard.comp_nr - 1].append(marked)

        self.left_utensils.toggle(None, mode="close")
        self.refresh_left()

    def pull_cards(self, *args):
        marked = []
        for compartment in self.l_slider_cards:
            marked += [card.flashcard for card in compartment if card.marked]

        database_f = Cache.get("app_info", "database_dir")
        FlashcardDataBase.strip_box(database_f, self.base_box_widget.box.id, marked)
        self.base_box_widget.box.nr_cards -= len(marked)

        to_remove = []
        for compartment in self.l_slider_cards:
            to_remove += [card for card in compartment if card.flashcard in marked]

        for card in to_remove:
            self.l_slider_cards[card.flashcard.comp_nr - 1].remove(card)

        self.refresh_left()
        self.left_utensils.toggle(None, mode="close")
        self.tags_dropdown.select(self.tags_container.children[0].tag)

        self.update_labels()
        self.base_box_widget.refresh()

    def push_cards(self, *args):
        marked = [card.flashcard for card in self.r_slider_cards if card.marked]

        database_f = Cache.get("app_info", "database_dir")
        FlashcardDataBase.update_compartment(database_f, self.base_box_widget.box.id, marked, None)
        self.base_box_widget.box.nr_cards += len(marked)

        for flashcard in marked:
            flashcard.comp_nr = 1
            s_card = SliderCard(flashcard)
            self.l_slider_cards[0].append(s_card)

        self.refresh_left()
        self.right_utensils.toggle(None, mode="close")
        self.tags_dropdown.select(self.tags_container.children[0].tag)

        self.update_labels()
        self.base_box_widget.refresh()
        self.pages.page = 0

    def hide_utensils(self, dropdown, page):

        if page == 0:
            self.right_utensils.toggle(None, mode="close")
            self.refresh_left_utensils()
        else:
            self.left_utensils.toggle(None, mode="close")
            self.refresh_right_utensils()

    def refresh_right_utensils(self, *args):
        marked = [card for card in self.r_slider_cards if card.marked]

        if not marked:
            self.right_utensils.toggle(None, mode="close")

        else:
            self.right_utensils.toggle(self.back_btn, "down", mode="open")

    def refresh_left_utensils(self, *args):
        marked = []
        for compartment in self.l_slider_cards:
            marked += [card for card in compartment if card.marked]

        if not marked:
            self.left_utensils.toggle(None, mode="close")

        elif len(marked) == 1:
            self.left_utensils.items["up_btn"].bind(on_release=self.shift_card)
            self.left_utensils.items["up_btn"].change_mode("enabled")
            self.left_utensils.items["down_btn"].bind(on_release=self.shift_card)
            self.left_utensils.items["down_btn"].change_mode("enabled")

            self.left_utensils.toggle(self.back_btn, "down", mode="open")

        else:
            self.left_utensils.items["up_btn"].unbind(on_release=self.shift_card)
            self.left_utensils.items["up_btn"].change_mode("disabled")
            self.left_utensils.items["down_btn"].unbind(on_release=self.shift_card)
            self.left_utensils.items["down_btn"].change_mode("disabled")

            self.left_utensils.toggle(self.back_btn, "down", mode="open")

    def refresh_left(self):
        self.left_container.clear_widgets()
        for comp_nr, compartment in enumerate(self.l_slider_cards, 1):
            comp_lbl = Label(text=str(comp_nr), size_hint=(1, None), height=self.left_container.width / 10,
                             color=get_color_from_hex("#444444"))
            self.left_container.add_widget(comp_lbl)

            for card in compartment:
                if card.marked:
                    card.toggle_marked()
                card.bind(pos=card.draw, width=card.adjust_style)
                card.bind(size=self.left_container.resize_v, on_hold=card.toggle_marked)
                card.bind(marked=self.refresh_left_utensils)
                self.left_container.add_widget(card)

        self.left_container.resize_v()
        self.left_container.bind(height=self.enable_disable_scroll)

        self.left_slider.scroll_y = 1

    def display_card(self, slider_card):
        display_s_card(slider_card, self.size)

    def refresh_right(self):
        self.right_container.clear_widgets()
        for card in self.r_slider_cards:
            if card.marked:
                card.toggle_marked()

            card.bind(pos=card.draw, width=card.adjust_style)
            card.bind(size=self.right_container.resize_v, on_hold=card.toggle_marked)
            card.bind(marked=self.refresh_right_utensils, on_choose=self.display_card)
            self.right_container.add_widget(card)

        self.right_container.bind(height=self.enable_disable_scroll)

        self.right_slider.scroll_y = 1

    def on_enter(self, *args):

        if not self.tags_dropdown.container.children:
            database_f = Cache.get("app_info", "database_dir")
            retrieved_tags = [Tag(0, "all cards", "AAAAAA")] + FlashcardDataBase.retrieve_tags(database_f)

            for index, tag in enumerate(retrieved_tags):
                slider_tag = SliderTag(tag, index)
                slider_tag.bind(pos=slider_tag.adjust_style, size=slider_tag.draw)
                slider_tag.bind(pos=slider_tag.draw)
                slider_tag.bind(on_choose=lambda slider_t: self.tags_dropdown.select(slider_t.tag))
                self.tags_dropdown.add_widget(slider_tag)

        work_dir = Cache.get("app_info", "work_dir") + "/data/textures"
        if self.left_utensils is None:
            self.left_utensils = UtensilDropUp(pos=(self.back_btn.x, self.back_btn.y))

            # preparing action buttons
            pull_btn = UtensilButton(work_dir + "/pull_icon.png",
                                     height=self.left_invisible.height, width=self.left_invisible.width)
            down_btn = UtensilButton(work_dir + "/down_icon.png",
                                     height=self.left_invisible.height, width=self.left_invisible.width)
            up_btn = UtensilButton(work_dir + "/up_icon.png",
                                   height=self.left_invisible.height, width=self.left_invisible.width)

            pull_btn.bind(pos=pull_btn.draw, on_release=self.pull_cards)
            down_btn.bind(pos=down_btn.draw)
            up_btn.bind(pos=up_btn.draw)

            self.left_utensils.items["up_btn"] = up_btn
            self.left_utensils.items["pull_btn"] = pull_btn
            self.left_utensils.items["down_btn"] = down_btn

            self.ids["back_btn_layout"].add_widget(self.left_utensils)

        if self.right_utensils is None:
            self.right_utensils = UtensilDropUp(pos=(self.back_btn.x, -dp(10)))

            # preparing action buttons
            push_btn = UtensilButton(work_dir + "/push_icon.png",
                                     height=self.right_invisible.height, width=self.right_invisible.width)

            push_btn.bind(pos=push_btn.draw, on_release=self.push_cards)

            self.right_utensils.items["push_btn"] = push_btn

            self.ids["back_btn_layout"].add_widget(self.right_utensils)

        # preparing all cards tag for initial setting
        all_cards_tag = next(
            s_tag.tag for s_tag in self.tags_dropdown.container.children if s_tag.tag.name == "all cards")
        Clock.schedule_once(lambda nt: self.tags_dropdown.select(all_cards_tag), 0.05)
        self.pages.bind(page=self.hide_utensils)

    def on_leave(self, *args):
        self.tags_dropdown.container.clear_widgets()
        self.l_slider_cards.clear()
        self.r_slider_cards.clear()

    def on_pre_enter(self, *args):
        base_box = Cache.get("box_display", "base_box")
        self.base_box_widget.box = base_box

        date = datetime.fromtimestamp(base_box.creation_date)
        self.created_lbl.text = f"created: \n{date.strftime('%d.%m.%Y')}"
        self.update_labels()

        self.tags_dropdown.bind(on_select=self.select_tag)
        self.tags_dropdown.container.padding = [dp(10), dp(10)]
        self.tags_dropdown.container.spacing = dp(10)
        self.tags_dropdown.container.size_hint_x = 1
        self.tags_dropdown.dismiss()

        self.pages.page = 1  # switching to right slider view

        database_f = Cache.get("app_info", "database_dir")
        for comp_nr in range(1, self.base_box_widget.box.nr_compartments + 1):
            retrieved_cards = FlashcardDataBase.retrieve_cards(database_f, "box",
                                                               box=self.base_box_widget.box.id, compartment=comp_nr)
            for card in retrieved_cards:
                card.comp_nr = comp_nr

            self.l_slider_cards.append([SliderCard(card) for card in retrieved_cards])

        Clock.schedule_once(lambda nt: self.base_box_widget.refresh(), 0.05)
        Clock.schedule_once(lambda nt: self.refresh_left(), 0.05)

    def __init__(self, **kwargs):
        super(BoxDisplayScreen, self).__init__(**kwargs)

        self.l_slider_cards = []
        self.r_slider_cards = []

        self.left_utensils = None
        self.right_utensils = None
