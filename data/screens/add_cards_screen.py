from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from data.flashcards.flashcard_database import Flashcard
from kivy.app import App
from kivy.utils import platform
from ..classes.otter_cards_config import OtterCardsConfig


class AddCardsScreen(Screen):

    def request_dict_perms(self):
        if platform != "win" and OtterCardsConfig.settings["granted_internet_permission"] == 0:
            from android.permissions import Permission, request_permissions

            def perms_callback(permission, results):
                if all([result for result in results]):
                    OtterCardsConfig.append("granted_internet_permission", 1)
                    OtterCardsConfig.save()
                    self.request_dict_perms()

            request_permissions([Permission.INTERNET], perms_callback)

        else:
            App.get_running_app().switch_screen("add_from_dictionary_screen", "left")

    def request_ocr_perms(self):
        if platform != "win" and OtterCardsConfig.settings["granted_camera_permission"] == 0:
            from android.permissions import Permission, request_permissions

            def perms_callback(permission, results):
                if all([result for result in results]):
                    OtterCardsConfig.append("granted_camera_permission", 1)
                    OtterCardsConfig.save()

                    # App.get_running_app().switch_screen("add_from_ocr_screen", "left")

            request_permissions([Permission.INTERNET, Permission.CAMERA], perms_callback)

        else:
            App.get_running_app().switch_screen("add_from_ocr_screen", "left")

    def add_manually(self):

        base_card = Flashcard(id=None, tags=[], def_lines=["", "", ""], hidden_lines=["", "", ""])

        Cache.append("card_workshop", "base_card", base_card)
        App.get_running_app().switch_screen("card_workshop_screen", "left")

    def __init__(self, **kwargs):
        super(AddCardsScreen, self).__init__(**kwargs)
