from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.utils import platform
from kivy.app import App
from ..classes.otter_cards_config import OtterCardsConfig as Cfg
from ..classes.popups import welcome_popup, ok_popup
from kivy.clock import Clock


class MainScreen(Screen):
    header = ObjectProperty()
    main_layout = ObjectProperty()
    icon = ObjectProperty()
    flashcards_btn = ObjectProperty()
    revising_btn = ObjectProperty()
    info_help_btn = ObjectProperty()

    def on_size(self, obj, size):
        if self.get_root_window() is not None:
            if self.get_root_window().width == self.width:
                self.welcome()

    def welcome(self):
        if self.welcome_popped:
            return

        if Cfg.settings["already_run_app"] == 0:

            pop = welcome_popup(self.size)
            Clock.schedule_once(lambda nt: pop.open(), 0.07)

            Cfg.append("already_run_app", 1)

        else:

            pop = ok_popup("Welcome! Happy to see you again and wish you fun with revising!", self.width)
            Clock.schedule_once(lambda nt: pop.open(), 0.07)

        self.welcome_popped = True

    def request_perms(self):
        if platform != "win" and Cfg.settings["granted_storage_permission"] == 0:
            from android.permissions import Permission, request_permissions

            def perms_callback(permission, results):
                if all([result for result in results]):
                    Cfg.append("granted_storage_permission", 1)

            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE], perms_callback)

        else:
            App.get_running_app().switch_screen("cards_screen", "left")

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.welcome_popped = False

        if Cfg.settings["already_run_app"]:
            self.welcome_popup_text = "Welcome! Happy to see you again and wish you fun with revising!"
        else:
            self.welcome_popup_text = "It seems that you are willing to find new learning methods. " \
                                      "To make the most out of this app, please read " \
                                      "short description available at 'info & help'."