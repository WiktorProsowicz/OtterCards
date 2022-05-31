from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.cache import Cache
from kivy.properties import ObjectProperty
from ..classes.dragged_flashcard import DraggedFlashcard
from ..flashcards.flashcard_database import FlashcardDataBase
from kivy.animation import Animation
from ..classes.popups import ok_popup, yes_no_popup


class RevisingScreen(Screen):

    main_layout = ObjectProperty(None)

    def go_back(self):

        info_pop = yes_no_popup("do you want to save the progress you've made?", self.width, 0.4,
                                lambda btn: self.complete_revising(),
                                lambda btn: App.get_running_app().switch_screen("revising_settings_screen", "right"))

        info_pop.open()

    def complete_revising(self):
        database_f = Cache.get("app_info", "database_dir")

        if self.box.is_special:
            box_index = 0
            for card in [card for card in self.flashcards if card not in self.correctly_answered]:
                if FlashcardDataBase.is_card_in_box(database_f, card, self.box):
                    continue

                FlashcardDataBase.update_compartment(database_f, self.dump_boxes[box_index].id, [card], None)
                box_index = (1 + box_index) % len(self.dump_boxes)

        FlashcardDataBase.update_compartment(database_f, self.box.id, self.correctly_answered, self.compartment)

        correct_ratio = len(self.correctly_answered) / len(self.flashcards)
        if correct_ratio <= 0.25:
            title = f"only {len(self.correctly_answered)}/{len(self.flashcards)} correct answers..."

        elif correct_ratio <= 0.5:
            title = f"not bad! you've answered correctly {len(self.correctly_answered)}/{len(self.flashcards)} questions"

        elif correct_ratio <= 0.8:
            title = f"good job! {len(self.correctly_answered)}/{len(self.flashcards)} questions answered correctly"

        else:
            title = f"amazing! {len(self.correctly_answered)}/{len(self.flashcards)} correct answers"

        ok_pop = ok_popup(title, self.width, 0.4, lambda btn: App.get_running_app().switch_screen("revising_settings_screen", "right"))
        ok_pop.open()

    def approve_card(self, correct: bool):
        if correct:
            self.correctly_answered.append(self.card_widget.flashcard)

        if self.current_card_index == len(self.flashcards) - 1:
            self.complete_revising()

        else:
            fade_anim = Animation(opacity=0, duration=.2)
            fade_anim.bind(on_complete=lambda sth1, sth2: self.load_next_card())
            fade_anim.start(self.card_widget)

    def on_leave(self, *args):
        self.flashcards.clear()
        self.correctly_answered.clear()

        self.card_widget.pos = (self.width * 0.12, -self.card_widget.height)    # hiding the card

    def load_next_card(self):
        self.current_card_index += 1
        self.card_widget.flashcard = self.flashcards[self.current_card_index]
        self.card_widget.reset((self.width * 0.12, -self.card_widget.height), self.show_def_side)

        target_pos =(self.width * 0.12, self.width * 0.72 + (self.height - self.width * 0.72 - self.card_widget.height) / 2)
        in_anim = Animation(pos=target_pos,
                            t="out_expo", duration=1.5)
        in_anim.start(self.card_widget)

    def on_enter(self, *args):
        if self.card_widget is None:
            self.card_widget = DraggedFlashcard((self.width * 0.75, self.height - self.width * 0.8),
                                                drag_rectangle=(self.main_layout.x, self.main_layout.width * 0.72,
                                                                self.main_layout.width, self.main_layout.height - self.main_layout.width * 0.72))
            self.card_widget.bind(on_incorrect=lambda card: self.approve_card(False))
            self.card_widget.bind(on_correct=lambda card: self.approve_card(True))
            self.main_layout.add_widget(self.card_widget)

        if self.flashcards:
            self.load_next_card()

        else:
            info_pop = ok_popup("it seems there is no card in this compartment", self.width, 0.35,
                                lambda btn: App.get_running_app().switch_screen("revising_settings_screen", "right"))
            info_pop.open()

    def on_pre_enter(self, *args):
        database_f = Cache.get("app_info", "database_dir")

        box_id = Cache.get("revising", "box")
        self.box = FlashcardDataBase.retrieve_boxes(database_f, id=box_id)[0]

        self.compartment = Cache.get("revising", "compartment")
        self.show_def_side = Cache.get("revising", "show_def")

        self.dump_boxes = Cache.get("revising", "dump_boxes")

        self.flashcards = FlashcardDataBase.retrieve_cards(database_f, "box", box=self.box.id, compartment=self.compartment)
        self.current_card_index = -1

    def __init__(self, **kwargs):
        super(RevisingScreen, self).__init__(**kwargs)

        self.flashcards = []
        self.correctly_answered = []

        self.box = None
        self.compartment = 0
        self.dump_boxes = []
        self.show_def_side = True

        self.current_card_index = -1
        self.card_widget = None
