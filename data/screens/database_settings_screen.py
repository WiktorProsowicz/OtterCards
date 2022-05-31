from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.cache import Cache
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from os.path import isdir
from .add_from_file_screen import AddFromFileScreen
from ..flashcards.flashcard_database import FlashcardDataBase
from ..classes.popups import ok_popup, yes_no_popup


class DatabaseSettingsScreen(Screen):

    title_label = ObjectProperty(None)
    filename_label = ObjectProperty(None)
    dirname_label = ObjectProperty(None)

    def save_backup(self):
        if self.selected_dir is None:
            return

        database_f = Cache.get("app_info", "database_dir")

        try:
            FlashcardDataBase.save_backup(database_f, self.selected_dir)

            confirm_pop = ok_popup("successfully created a database backup file", screen_width=self.width, height_hint=0.4)
            confirm_pop.open()

        except:
            warning_pop = ok_popup("something went wrong while saving the backup", screen_width=self.width)
            warning_pop.open()

    def upload_backup(self):
        if self.selected_file is None:
            return

        aux_database_f = Cache.get("app_info", "aux_database_dir")

        try:
            FlashcardDataBase.upload_backup(aux_database_f, self.selected_file)
            App.get_running_app().switch_screen("backup_content_screen", "left")

        except:
            warning_pop = ok_popup("something went wrong... maybe you provided invalid file?", screen_width=self.width)
            warning_pop.open()

    def warn_before_clearing(self):

        info_pop = yes_no_popup("are you sure? changes cannot be reversed", self.width, 0.35,
                                lambda obj: self.clear_database())
        info_pop.open()

    def clear_database(self):
        database_f = Cache.get("app_info", "database_dir")
        FlashcardDataBase.clear_database(database_f)

    def select_dir(self, selection):
        # /// VALIDATION MAY BE NEEDED!

        if not selection:
            return

        self.selected_dir = selection[0]
        self.dirname_label.text = selection[0]

    def filter_file(self, folder, file):
        return isdir(file)

    def select_file(self, selection):
        AddFromFileScreen.select_file(self, selection)

    def show_files(self):
        AddFromFileScreen.show_files(self)

    def show_directories(self):
        workdir = Cache.get("app_info", "work_dir")
        rootpath = Cache.get("app_info", "rootpath")

        # preparing file_chooser popup
        # filechooser progress is "muted" in main_layout.kv by setting opacity to 0
        pop_content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(10))
        filechooser = FileChooserIconView(filters=[self.filter_file], size_hint=(1, 0.9), rootpath=rootpath,
                                          show_hidden=True, dirselect=True)
        filechooser_popup = Popup(title="choose directory", title_align="center", separator_color=(0, 0, 0, 1),
                                  size_hint=(0.9, 0.6), title_color=get_color_from_hex("#444444"),
                                  background=workdir + "/data/textures/popup_background.png",
                                  title_size=self.title_label.font_size * 0.8, content=pop_content,
                                  border=[0, 0, 0, 0])
        btn = Button(text="submit", color=get_color_from_hex("#444444"),
                     font_size=self.title_label.font_size * 0.6,
                     background_normal=workdir + "/data/textures/yes_button_normal.png",
                     background_down=workdir + "/data/textures/yes_button_down.png", opacity=0.7,
                     size_hint=(0.5, None), pos_hint={"center_x": 0.5})

        pop_content.add_widget(filechooser)
        pop_content.add_widget(btn)

        btn.height = btn.font_size * 2.5

        btn.bind(on_release=lambda btn: self.select_dir(filechooser.selection))
        btn.bind(on_release=filechooser_popup.dismiss)

        filechooser_popup.open()

    def on_pre_enter(self, *args):

        self.selected_dir = None
        self.dirname_label.text = "no directory chosen yet"
        self.selected_file = None
        self.filename_label.text = "no file chosen yet"

    def __init__(self, **kwargs):
        super(DatabaseSettingsScreen, self).__init__(**kwargs)

        self.selected_dir = None
        self.selected_file = None