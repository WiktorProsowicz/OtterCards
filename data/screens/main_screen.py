from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.graphics import Rectangle
from kivy.cache import Cache
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button


class MainScreen(Screen):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # self.size = Cache.get("app_info", "dev_res")

        self.header = ObjectProperty()
        self.main_layout = ObjectProperty()
        self.icon = ObjectProperty()
        self.flashcards_btn = ObjectProperty()
        self.revising_btn = ObjectProperty()
        self.info_help_btn = ObjectProperty()


