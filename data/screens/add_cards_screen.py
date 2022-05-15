from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from data.flashcards.flashcard_database import Flashcard
from kivy.app import App


class AddCardsScreen(Screen):

    def add_manually(self):

        base_card = Flashcard(id=None, tags=[], def_lines=["", "", ""], hidden_lines=["", "", ""])

        Cache.append("card_workshop", "base_card", base_card)
        App.get_running_app().switch_screen("card_workshop_screen", "left")

    def __init__(self, **kwargs):
        super(AddCardsScreen, self).__init__(**kwargs)
