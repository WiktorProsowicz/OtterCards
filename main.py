from kivy.app import App
from kivy.config import Config
from os import curdir, path, environ

Config.read("data/config/OtterCards.ini")
environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.cache import Cache
from kivy.utils import platform
from kivy import require
from kivy.core.window import Window

import ctypes

# importing screens
from data.screens import AddCardsScreen, AddFromDictionaryScreen, AddFromFileScreen, AddFromOcrScreen, BackupContentScreen, \
    BoxDisplayScreen, BoxWorkshopScreen, BoxesCollectionScreen, CardChunksScreen, CardWaitingRoomScreen, \
    CardWorkshopScreen, CardsCollectionScreen, CardsScreen, DatabaseSettingsScreen, DictWaitingRoomScreen, \
    MainScreen, RevisingScreen, RevisingSettingsScreen, TagWorkshopScreen, TagsCollectionScreen, InfoHelpScreen

from data.flashcards.flashcard_database import FlashcardDataBase

require("2.1.0")


class WindowManager(ScreenManager):

    def blur(self, transition, progression):
        transition.screen_in.opacity = progression
        transition.screen_out.opacity = 1 - progression

    def on_current(self, instance, value):
        self.old = self.new
        self.new = value
        super(WindowManager, self).on_current(instance, value)

    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        self.transition.bind(on_progress=self.blur)

        # screen names to handle returning to previous screen
        self.new = None
        self.old = None


class OtterCardsApp(App):

    def switch_screen(self, screen_name, direction):
        # var screen_name has to store the name of the screen we want to switch to
        # the name is always name of the instance of the screen lowercase, eg. MAIN_S -> main_s
        direction_map = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left"
        }
        if direction == "inverted":
            self.window_manager.transition.direction = direction_map[self.window_manager.transition.direction]
        else:
            self.window_manager.transition.direction = direction

        if screen_name in self.window_manager.screen_names:
            self.window_manager.current = screen_name
        elif screen_name == "previous":
            self.window_manager.current = self.window_manager.old

    def on_pause(self):
        return True

    def on_start(self):
        aux_database_f = Cache.get("app_info", "aux_database_dir")
        FlashcardDataBase.clear_database(aux_database_f)

    def on_stop(self):
        pass

    def go_back(self, window, key, *largs):
        if key == 27 and hasattr(self.window_manager.current_screen, "back_btn"):
            self.window_manager.current_screen.back_btn.dispatch("on_release")

    def build_config(self, config):
        # registering all important cache's
        Cache.register("app_info")  # platform, work_dir, database_dir, aux_database_dir, rootpath
        Cache.register("tag_workshop")  # base_tag,
        Cache.register("cards_collection")  # main_filter,
        Cache.register("card_workshop")  # base_card, aux_mode
        Cache.register("card_waiting_room")  # card_ids
        Cache.register("dict_waiting_room")  # card_ids, extras, exceptions, language_mode,
        # subdefs_limit, cards_limit, get_hinted, dictionary
        Cache.register("card_chunks")   # new_chunk
        Cache.register("box_display")   # base_box
        Cache.register("box_workshop")   # base_box
        Cache.register("revising")  # box, compartment, show_def, dump_boxes
        # ...

        # saving values to app_info
        Cache.append("app_info", "platform", platform)
        Cache.append("app_info", "work_dir", path.abspath(curdir))
        # Cache.append("app_info", "database_dir", path.abspath(curdir) + "/data/OtterCardsDB.db")
        # Cache.append("app_info", "aux_database_dir", path.abspath(curdir) + "/data/OtterCardsAuxDB.db")
        Cache.append("app_info", "database_dir", path.abspath(curdir) + "/data/sample_database.db")
        Cache.append("app_info", "aux_database_dir", path.abspath(curdir) + "/data/sample_database_aux.db")

        if Cache.get("app_info", "platform") == "win":
            user32 = ctypes.windll.user32
            s_width, s_height = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)

            Config.set("graphics", "width", int(s_width * 0.9))
            Config.set("graphics", "height", int(s_width * 0.9))
            Cache.append("app_info", "rootpath", "C:/Users")

            # ///// for developer /////////
            Config.set("graphics", "width", 380)
            Config.set("graphics", "height", 736)
            # /////////////////////////////

            # Config.write()

        else:
            Cache.append("app_info", "rootpath", "/storage/emulated/0")
            from android.permissions import Permission, request_permissions

            def perms_callback(permission, results):
                if not all([result for result in results]):
                    self.stop()

            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE,
                                 Permission.CAMERA, Permission.INTERNET], perms_callback)

    def build(self):
        # getting window size regardless of the platform
        # s_width, s_height = Window.size
        # s_width = s_width / Window.dpi * 96
        #
        # if s_width < 576:
        #     prefix = "xs"
        # elif s_width < 768:
        #     prefix = "sm"
        # elif s_width < 992:
        #     prefix = "md"
        # elif s_width < 1200:
        #     prefix = "lg"
        # elif s_width < 1400:
        #     prefix = "xl"
        # else:
        #     prefix = "xxl"

        prefix = "xs"
        Cache.append("app_info", "size_prefix", prefix)

        # loading all kv files
        screen_names = ["main_screen", "cards_screen", "tags_collection_screen", "tag_workshop_screen",
                        "cards_collection_screen", "add_cards_screen", "card_workshop_screen", "add_from_file_screen",
                        "card_waiting_room_screen", "add_from_dictionary_screen", "dict_waiting_room_screen",
                        "add_from_ocr_screen", "card_chunks_screen", "boxes_collection_screen", "box_display_screen",
                        "box_workshop_screen", "database_settings_screen", "backup_content_screen",
                        "revising_settings_screen", "revising_screen", "info_help_screen"]  # ...

        path_to_kv = Cache.get("app_info", "work_dir") + "/data/kv/" + Cache.get("app_info", "size_prefix") + "_"
        kv_filenames = [path_to_kv + name + ".kv" for name in screen_names]

        Builder.load_file(Cache.get("app_info", "work_dir") + "/data/kv/main_layout.kv")
        for filename in kv_filenames:
            Builder.load_file(filename)
        # ...

        # creating instances of all screens and adding to window manager
        screen_list = [MainScreen(name="main_screen"),
                       CardsScreen(name="cards_screen"),
                       TagsCollectionScreen(name="tags_collection_screen"),
                       TagWorkshopScreen(name="tag_workshop_screen"),
                       CardsCollectionScreen(name="cards_collection_screen"),
                       AddCardsScreen(name="add_cards_screen"),
                       CardWorkshopScreen(name="card_workshop_screen"),
                       AddFromFileScreen(name="add_from_file_screen"),
                       CardWaitingRoomScreen(name="card_waiting_room_screen"),
                       AddFromDictionaryScreen(name="add_from_dictionary_screen"),
                       DictWaitingRoomScreen(name="dict_waiting_room_screen"),
                       AddFromOcrScreen(name="add_from_ocr_screen"),
                       CardChunksScreen(name="card_chunks_screen"),
                       BoxesCollectionScreen(name="boxes_collection_screen"),
                       BoxDisplayScreen(name="box_display_screen"),
                       BoxWorkshopScreen(name="box_workshop_screen"),
                       DatabaseSettingsScreen(name="database_settings_screen"),
                       BackupContentScreen(name="backup_content_screen"),
                       RevisingSettingsScreen(name="revising_settings_screen"),
                       RevisingScreen(name="revising_screen"),
                       InfoHelpScreen(name="info_help_screen")]

        self.window_manager = WindowManager(transition=SlideTransition())

        for screen in screen_list:
            self.window_manager.add_widget(screen)
        # ...

        # /// dev /////////////////////////////////////////
        # self.window_manager.current = "add_from_dictionary_screen"
        # ///////////////////////////////////////////////

        Window.bind(on_keyboard=self.go_back)

        self.icon = Cache.get("app_info", "work_dir") + "/data/textures/logo.png"
        self.title = "OtterCardsApp"
        return self.window_manager

    def __init__(self, **kwargs):
        super(OtterCardsApp, self).__init__(**kwargs)
        self.window_manager = None  # instance is created in build method so that kv rules can be aplied to window manager


if __name__ == "__main__":
    OtterCardsApp().run()
