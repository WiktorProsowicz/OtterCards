from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from kivy.properties import ObjectProperty
from data.flashcards.flashcard_database import FlashcardDataBase
from kivy.utils import get_color_from_hex
from kivy.app import App
from ..classes.smart_input import SmartInput
from kivy.metrics import dp
from ..classes.utensils import UtensilDropUp, UtensilButton
from ..classes.horizontal_slider_tag import HorizontalSliderTag
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.popup import Popup
from ..classes.smart_grid_layout import SmartGridLayout
from ..classes.slider_tag import SliderTag
from kivy.uix.label import Label
from ..classes.utils import a_difference_b
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class CardWorkshopScreen(Screen):
    title_label = ObjectProperty(None)
    tags_container = ObjectProperty(None)
    lines_container = ObjectProperty(None)
    lines_slider = ObjectProperty(None)
    tags_slider = ObjectProperty(None)
    more_btn = ObjectProperty(None)
    lines_label = ObjectProperty(None)
    main_layout = ObjectProperty(None)

    def save(self):
        if Cache.get("card_workshop", "aux_mode"):
            database_f = Cache.get("app_info", "aux_database_dir")
        else:
            database_f = Cache.get("app_info", "database_dir")
        workdir = Cache.get("app_info", "work_dir")

        return_message = FlashcardDataBase.insert_cards(database_f, [self.base_card])
        if return_message == "LengthError":
            btn = Button(text="ok", color=get_color_from_hex("#444444"),
                         font_size=self.title_label.font_size * 0.6,
                         background_normal=workdir + "/data/textures/yes_button_normal.png",
                         background_down=workdir + "/data/textures/yes_button_down.png", opacity=0.7)
            warning_pop = Popup(title="some of the lines are too long! consider separating them into new ones",
                                auto_dismiss=True,
                                size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                                title_color=get_color_from_hex("#444444"),
                                background=workdir + "/data/textures/popup_background.png",
                                title_size=self.title_label.font_size * 0.7, height=self.width * 0.9 / 2,
                                content=btn, border=[0, 0, 0, 0])
            btn.bind(on_release=warning_pop.dismiss)

            warning_pop.open()

        else:
            App.get_running_app().switch_screen("previous", "inverted")

    def leave_workshop(self, mode: str):

        self.update_card()

        # checking whether init_card ans base_card are the same
        if a_difference_b(self.init_card.def_lines, self.base_card.def_lines) or \
                a_difference_b(self.base_card.def_lines, self.init_card.def_lines) or \
                a_difference_b(self.init_card.hidden_lines, self.base_card.hidden_lines) or \
                a_difference_b(self.base_card.hidden_lines, self.init_card.hidden_lines) or \
                set(self.init_card.tags) != set(self.base_card.tags):
            base_same_init = False
        else:
            base_same_init = True

        workdir = Cache.get("app_info", "work_dir")

        if base_same_init:
            App.get_running_app().switch_screen("previous", "inverted")

        elif mode == "approve":
            self.save()

        elif mode == "back":
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

    def update_card(self, *args):

        if self.mode == "hidden":
            self.base_card.hidden_lines.clear()
        else:
            self.base_card.def_lines.clear()

        for line_input in self.line_inputs:
            if self.mode == "hidden":
                self.base_card.hidden_lines.append(line_input.text)
            else:
                self.base_card.def_lines.append(line_input.text)

        self.base_card.tags.clear()
        for slider_tag in self.slider_tags:
            self.base_card.tags.append(slider_tag.tag.name)

    def delete_marked(self):
        self.update_card()

        # deleting marked lines
        for line_input in self.line_inputs:
            if line_input.marked:
                if self.mode == "hidden":
                    self.base_card.hidden_lines.remove(line_input.text)
                else:
                    self.base_card.def_lines.remove(line_input.text)

        # deleting marked tags
        for slider_tag in self.slider_tags:
            if slider_tag.marked:
                self.base_card.tags.remove(slider_tag.tag.name)

        if self.utensils.open:
            self.utensils.toggle(None)

        self.refresh_lines()
        self.refresh_tags()

    def add_line(self):
        if self.mode == "hidden":
            self.base_card.hidden_lines.append("")
        else:
            self.base_card.def_lines.append("")

        self.refresh_lines()

    def add_tag(self, slider_tag):
        self.base_card.tags.append(slider_tag.tag.name)

        self.refresh_tags()

    def show_tags(self):

        if self.utensils.open:
            self.utensils.toggle(None)

        # preparing tag popup
        tag_container = SmartGridLayout(cols=1, spacing=dp(10), size_hint=(1, None), padding=[0, dp(10)])
        slider = ScrollView(size=(self.main_layout.width * 0.9, self.main_layout.height * 0.5),
                            do_scroll_x=False, effect_y=ScrollEffect(), bar_inactive_color=(0, 0, 0, 0),
                            pos_hint={"y": 0}, bar_color=(0, 0, 0, 0))

        database_dir = Cache.get("app_info", "database_dir")
        workdir = Cache.get("app_info", "work_dir")

        slider.add_widget(tag_container)

        tags_popup = Popup(title="choose tag", auto_dismiss=True,
                           size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 1),
                           title_color=get_color_from_hex("#444444"),
                           background=workdir + "/data/textures/popup_background.png",
                           title_size=self.title_label.font_size * 0.8, content=slider,
                           border=[0, 0, 0, 0])
        tags_popup.height += slider.height + dp(20)

        retrieved_tags = FlashcardDataBase.retrieve_tags(database_dir, not_names=self.base_card.tags.copy())

        if retrieved_tags:
            for index, tag in enumerate(retrieved_tags, 1):
                slider_tag = SliderTag(tag, index)
                slider_tag.bind(size=lambda obj, pos: obj.draw(), pos=lambda obj, pos: obj.adjust_style())
                slider_tag.bind(pos=lambda obj, pos: tag_container.resize_v(),
                                on_choose=lambda obj: self.add_tag(obj))
                slider_tag.bind(on_choose=lambda obj: tags_popup.dismiss())
                tag_container.add_widget(slider_tag)

        else:
            text = "there are no tags left"
            so_empty_lbl = Label(text=text, size_hint=(1, None),
                                 pos_hint={"center_y": 0.5, "center_x": 0.5},
                                 color=get_color_from_hex("#444444"), font_size=self.lines_slider.width * 0.07)
            tags_popup.separator_color = (0, 0, 0, 1)
            tag_container.add_widget(so_empty_lbl)
            tags_popup.height -= slider.height - so_empty_lbl.height

        tag_container.resize_v()

        if tag_container.height > slider.height:
            slider.do_scroll_y = True
        else:
            slider.do_scroll_y = False

        tags_popup.open()

    def swap(self):
        self.update_card()

        self.mode = "hidden" if self.mode == "def" else "def"

        if self.utensils.open:
            self.utensils.toggle(None)

        self.refresh_lines()

    def on_leave(self, *args):
        self.lines_container.clear_widgets()
        self.line_inputs.clear()
        if self.utensils.open:
            self.utensils.toggle(None)

    def refresh_lines(self):
        workdir = Cache.get("app_info", "work_dir")
        lines = self.base_card.hidden_lines if self.mode == "hidden" else self.base_card.def_lines

        self.lines_label.text = "hidden side" if self.mode == "hidden" else "definition side"

        self.lines_container.clear_widgets()
        self.line_inputs.clear()

        for line in lines:
            line_input = SmartInput(workdir + "/data/textures/line_input_marked.png", text=line, size_hint=(1, None),
                                    font_size=1,
                                    height=1, do_wrap=True, multiline=True, halign="left",
                                    valign="middle", padding=(self.lines_container.width / 15, dp(6)),
                                    foreground_color=get_color_from_hex("#444444"),
                                    background_normal=workdir + f"/data/textures/{self.mode}_line_input_normal.png",
                                    background_active=workdir + "/data/textures/line_input_focused.png")
            self.line_inputs.append(line_input)

        for line_input in self.line_inputs:
            line_input.bind(pos=lambda obj, size: self.lines_container.resize_v(), text=lambda obj, text: obj.resize())
            line_input.bind(line_height=lambda obj, text: obj.resize(), on_hold=lambda obj: obj.toggle_marked())
            line_input.bind(focus=lambda l_input, focus: self.update_card() if not focus else None)
            self.lines_container.add_widget(line_input)

        self.lines_container.resize_v()
        self.enable_disable_scroll_v()

        self.lines_slider.scroll_y = 1

    def refresh_tags(self):
        database_dir = Cache.get("app_info", "database_dir")
        tags = FlashcardDataBase.retrieve_tags(database_dir, names=self.base_card.tags.copy())

        self.slider_tags.clear()
        self.tags_container.clear_widgets()

        for tag in tags:
            self.slider_tags.append(HorizontalSliderTag(tag))

        self.tags_container.cols = len(self.slider_tags)
        for slider_tag in self.slider_tags:
            slider_tag.bind(pos=lambda obj, pos: obj.adjust_style(), height=lambda obj, pos: obj.adjust_style())
            slider_tag.bind(width=lambda obj, pos: self.tags_container.resize_h(), size=lambda obj, size: obj.draw())
            slider_tag.bind(on_hold=slider_tag.toggle_marked)
            self.tags_container.add_widget(slider_tag)

        self.tags_container.resize_h()
        self.enable_disable_scroll_h()

        self.tags_slider.scroll_x = 0

    def on_pre_enter(self, *args):
        # setting base and initial cards
        self.base_card = Cache.get("card_workshop", "base_card")
        self.init_card = self.base_card.__copy__()

        self.title_label.text = "create card" if self.base_card.id is None else "edit card"

        self.tags_container.bind(size=lambda obj, size: self.enable_disable_scroll_h())
        self.lines_container.bind(size=lambda obj, size: self.enable_disable_scroll_v())

        self.refresh_lines()
        self.refresh_tags()

    def on_enter(self, *args):
        # initializing utensils (in on_enter because otherwise utensils might have wrong size)
        if self.utensils is None:
            self.utensils = UtensilDropUp(pos=(self.more_btn.x, -dp(10)))

            # preparing action buttons
            work_dir = Cache.get("app_info", "work_dir") + "/data/textures"
            delete_btn = UtensilButton(work_dir + "/delete_icon.png",
                                       height=self.more_btn.height, width=self.more_btn.width)
            add_tag_btn = UtensilButton(work_dir + "/add_tag_icon.png",
                                        height=self.more_btn.height, width=self.more_btn.width)
            add_line_btn = UtensilButton(work_dir + "/add_line_icon.png",
                                         height=self.more_btn.height, width=self.more_btn.width)
            swap_btn = UtensilButton(work_dir + "/swap_icon.png",
                                     height=self.more_btn.height, width=self.more_btn.width)

            delete_btn.bind(pos=delete_btn.draw, on_release=lambda btn: self.delete_marked())
            add_tag_btn.bind(pos=add_tag_btn.draw, on_release=lambda btn: self.show_tags())
            add_line_btn.bind(pos=add_line_btn.draw, on_release=lambda btn: self.add_line())
            swap_btn.bind(pos=swap_btn.draw, on_release=lambda btn: self.swap())

            self.utensils.items["delete_btn"] = delete_btn
            self.utensils.items["add_tag_btn"] = add_tag_btn
            self.utensils.items["add_line_btn"] = add_line_btn
            self.utensils.items["swap_btn"] = swap_btn

            self.more_btn.bind(on_release=self.utensils.toggle)
            self.ids["additional_layout"].add_widget(self.utensils)

    def enable_disable_scroll_v(self):
        self.lines_slider.do_scroll_y = False if self.lines_container.height < self.lines_slider.height else True
        if self.lines_slider.height > self.lines_container.height:
            self.lines_slider.scroll_y = 1

    def enable_disable_scroll_h(self):
        self.tags_slider.do_scroll_x = False if self.tags_container.width < self.tags_slider.width else True

    def __init__(self, **kwargs):
        super(CardWorkshopScreen, self).__init__(**kwargs)

        self.base_card = None  # card that is currently being edited or created
        self.init_card = None  # to compare initial card with current state of base_card on leave

        self.line_inputs = []  # list of currently displayed lines
        self.slider_tags = []  # list of currently present tags

        self.utensils = None

        self.mode = "hidden"    # indicates side of the base card that is being shown
