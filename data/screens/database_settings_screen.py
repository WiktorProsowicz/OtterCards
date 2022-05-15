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


class DatabaseSettingsScreen(Screen):

    title_label = ObjectProperty(None)
    filename_label = ObjectProperty(None)
    dirname_label = ObjectProperty(None)

    def save_backup(self):
        if self.selected_dir is None:
            return

        try:
            database_f = Cache.get("app_info", "database_dir")
            FlashcardDataBase.save_backup(database_f, self.selected_dir)

        except:
            print("error")

    def upload_backup(self):
        if self.selected_file is None:
            return

        try:
            print(FlashcardDataBase.upload_backup(self.selected_file))

        except:
            print("error")

    def select_dir(self, dirpath):
        # /// VALIDATION MAY BE NEEDED!

        self.selected_dir = dirpath
        self.dirname_label.text = dirpath

    def filter_file(self, folder, file):
        return isdir(file)

    def select_file(self, filepath):
        AddFromFileScreen.select_file(self, filepath)

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

        btn.bind(on_release=lambda btn: self.select_dir(filechooser.selection[0]))
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