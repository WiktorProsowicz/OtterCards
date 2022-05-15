from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty
from data.flashcards.flashcard_database import FlashcardDataBase
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.metrics import dp


class TagWorkshopScreen(Screen):
    title_label = ObjectProperty(None)
    color_label = ObjectProperty(None)

    base_tag_widget = ObjectProperty(None)
    name_input = ObjectProperty(None)

    red_slider = ObjectProperty(None)
    green_slider = ObjectProperty(None)
    blue_slider = ObjectProperty(None)

    def save(self):
        database_dir = Cache.get("app_info", "database_dir")
        workdir = Cache.get("app_info", "work_dir")

        if self.base_tag_widget.tag != "all cards":
            return_message = FlashcardDataBase.insert_tag(database_dir, self.base_tag_widget.tag)
        else:
            return_message = "NameError"    # can't create a tag with this name so an error is raised

        if return_message == "NameError" or return_message == "LengthError":
            title = "this name is taken!" if return_message == "NameError" else "this name has invalid length!"

            btn = Button(text="ok", color=get_color_from_hex("#444444"), font_size=self.title_label.font_size * 0.6,
                         background_normal=workdir + "/data/textures/yes_button_down.png",
                         background_down=workdir + "/data/textures/button_down.png", opacity=0.5)
            warning_pop = Popup(title=title, auto_dismiss=True,
                                size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                                title_color=get_color_from_hex("#444444"),
                                background=workdir + "/data/textures/popup_background.png",
                                title_size=self.title_label.font_size * 0.7, height=self.width * 0.9 / 3,
                                content=btn, border=[0, 0, 0, 0])
            btn.bind(on_release=warning_pop.dismiss)

            warning_pop.open()

        else:
            App.get_running_app().switch_screen("previous", "inverted")

    def leave_workshop(self, mode: str):
        # set current tag info
        base_info = [self.base_tag_widget.tag.name, self.base_tag_widget.tag.color]
        workdir = Cache.get("app_info", "work_dir")

        if self.init_info != base_info or mode == "save":
            if mode == "back":
                pop_content = BoxLayout(orientation="horizontal", spacing=dp(10))
                yes_btn = Button(text="yes", color=get_color_from_hex("#444444"),
                                 font_size=self.title_label.font_size * 0.6,
                                 background_normal=workdir + "/data/textures/yes_button_normal.png",
                                 background_down=workdir + "/data/textures/yes_button_down.png", opacity=0.7)
                no_btn = Button(text="no", color=get_color_from_hex("#444444"),
                                font_size=self.title_label.font_size * 0.6,
                                background_normal=workdir + "/data/textures/no_button_normal.png",
                                background_down=workdir + "/data/textures/no_button_down.png", opacity=0.7)
                pop_content.add_widget(yes_btn)
                pop_content.add_widget(no_btn)

                workdir = Cache.get("app_info", "work_dir")
                info_pop = Popup(title="do you want to save changes?", content=pop_content, auto_dismiss=True,
                                 size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                                 title_color=get_color_from_hex("#444444"),
                                 background=workdir + "/data/textures/popup_background.png",
                                 title_size=self.title_label.font_size * 0.6, height=self.width * 0.9 / 3,
                                 border=[0, 0, 0, 0])
                pop_content.bind(on_press=info_pop.dismiss)
                yes_btn.bind(on_release=lambda obj: self.save())
                no_btn.bind(
                    on_release=lambda obj: App.get_running_app().switch_screen("previous", "inverted"))

                yes_btn.bind(on_release=info_pop.dismiss)
                no_btn.bind(on_release=info_pop.dismiss)

                info_pop.open()

            else:
                self.save()
        else:
            App.get_running_app().switch_screen("previous", "inverted")

    def update_color_label(self):
        self.color_label.text = "color #" + self.base_tag_widget.tag.color

    def on_enter(self, *args):
        self.base_tag_widget.refresh()

    def on_pre_enter(self, *args):
        base_tag = Cache.get("tag_workshop", "base_tag")
        self.base_tag_widget.tag = base_tag
        self.init_info = [base_tag.name, base_tag.color]

        self.title_label.text = "create tag" if base_tag.id is None else "edit tag"

        init_col = self.base_tag_widget.tag.color
        r, g, b = init_col[0:2], init_col[2:4], init_col[4:6]

        r, g, b = int("0x" + r, 16), int("0x" + g, 16), int("0x" + b, 16)

        self.red_slider.value = r
        self.green_slider.value = g
        self.blue_slider.value = b

        self.name_input.text = self.base_tag_widget.tag.name

        self.color_label.text = "color #" + self.base_tag_widget.tag.color

        if not self.settings_bound:
            self.red_slider.bind(value=lambda slider, value: self.base_tag_widget.change_color("red", int(value)))
            self.green_slider.bind(value=lambda slider, value: self.base_tag_widget.change_color("green", int(value)))
            self.blue_slider.bind(value=lambda slider, value: self.base_tag_widget.change_color("blue", int(value)))

            self.red_slider.bind(value=lambda slider, value: self.update_color_label())
            self.green_slider.bind(value=lambda slider, value: self.update_color_label())
            self.blue_slider.bind(value=lambda slider, value: self.update_color_label())

            self.name_input.bind(text=lambda text_input, text: self.base_tag_widget.change_name(text))

            self.settings_bound = True

    def __init__(self, **kwargs):
        super(TagWorkshopScreen, self).__init__(**kwargs)

        self.init_info = None  # list important to determine if any changes were made
        self.settings_bound = False     # whether text, slider etc have functions bound to properties
