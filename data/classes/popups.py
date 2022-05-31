from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.cache import Cache
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from ..classes.smart_grid_layout import SmartGridLayout
from kivy.effects.scroll import ScrollEffect
from .slider_card import SliderCard
from ..flashcards.flashcard_database import FlashcardDataBase
from .slider_tag import SliderTag
from kivy.uix.label import Label
from .slider_box import SliderBox
from kivy.uix.floatlayout import FloatLayout
from .language_button import LanguageButton
from .menu_btn import MenuButton


def ok_popup(title: str, screen_width: float, height_hint=0.45, btn_callback=None):
    workdir = Cache.get("app_info", "work_dir")
    popup_text = title

    btn = Button(text="ok", color=get_color_from_hex("#444444"),
                 font_size=screen_width * 0.8 * 0.12 * 0.6,
                 background_normal=workdir + "/data/textures/yes_button_normal.png",
                 background_down=workdir + "/data/textures/yes_button_down.png", opacity=0.7)
    ok_pop = Popup(title=popup_text,
                   auto_dismiss=False,
                   size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                   title_color=get_color_from_hex("#444444"),
                   background=workdir + "/data/textures/popup_background.png",
                   title_size=screen_width * 0.8 * 0.12 * 0.6, height=screen_width * height_hint,
                   content=btn, border=[0, 0, 0, 0])
    btn.bind(on_release=ok_pop.dismiss)

    if btn_callback is not None:
        btn.bind(on_release=btn_callback)

    return ok_pop


def loading_popup(title: str, screen_width: float, height_hint=0.45):
    workdir = Cache.get("app_info", "work_dir")
    wheel = Image(source=workdir + "/data/textures/loading_screen.png",
                  allow_stretch=True, pos_hint={"center_x": 0.5, "center_y": 0.5})
    loading_pop = Popup(title=title, auto_dismiss=False,
                        size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 1),
                        title_color=get_color_from_hex("#444444"),
                        background=workdir + "/data/textures/popup_background.png",
                        title_size=screen_width * 0.1 * 0.7, height=screen_width * height_hint,
                        content=wheel, border=[0, 0, 0, 0])
    return loading_pop


def yes_no_popup(title: str, screen_width: float, height_hint=0.5, yes_callback=None, no_callback=None):
    workdir = Cache.get("app_info", "work_dir")

    pop_content = BoxLayout(orientation="horizontal", spacing=dp(10))
    yes_btn = Button(text="yes", color=get_color_from_hex("#444444"),
                     font_size=screen_width * 0.1 * 0.6,
                     background_normal=workdir + "/data/textures/yes_button_normal.png",
                     background_down=workdir + "/data/textures/yes_button_down.png", opacity=0.7)
    no_btn = Button(text="no", color=get_color_from_hex("#444444"),
                    font_size=screen_width * 0.1 * 0.6,
                    background_normal=workdir + "/data/textures/no_button_normal.png",
                    background_down=workdir + "/data/textures/no_button_down.png", opacity=0.7)
    pop_content.add_widget(yes_btn)
    pop_content.add_widget(no_btn)

    workdir = Cache.get("app_info", "work_dir")
    info_pop = Popup(title=title, content=pop_content, auto_dismiss=True,
                     size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                     title_color=get_color_from_hex("#444444"),
                     background=workdir + "/data/textures/popup_background.png",
                     title_size=screen_width * 0.1 * 0.6, height=screen_width * height_hint,
                     border=[0, 0, 0, 0])

    if yes_callback is not None:
        yes_btn.bind(on_release=yes_callback)

    if no_callback is not None:
        no_btn.bind(on_release=no_callback)

    yes_btn.bind(on_release=info_pop.dismiss)
    no_btn.bind(on_release=info_pop.dismiss)

    return info_pop


def card_display_popup(screen_width: float, height_hint=0.5):
    workdir = Cache.get("app_info", "work_dir")

    slider = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=True, effect_y=ScrollEffect(),
                        bar_inactive_color=(0, 0, 0, 0), bar_color=(0, 0, 0, 0))
    container = SmartGridLayout(cols=1, size_hint=(1, None))
    slider.add_widget(container)

    pop = Popup(title="",
                auto_dismiss=True,
                size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                title_color=get_color_from_hex("#444444"),
                background=workdir + "/data/textures/popup_background_transparent.png",
                title_size=0, height=screen_width * height_hint,
                content=slider, border=[0, 0, 0, 0])

    return pop, container


def display_card(slider_card, screen_size):
    card_copy = SliderCard(slider_card.flashcard)

    # hint = len(slider_card.flashcard.def_lines) + len(slider_card.flashcard.hidden_lines)
    # hint /= 7
    # hint = 2 if hint > 2 else hint

    pop, container = card_display_popup(screen_size[0])

    card_copy.bind(pos=card_copy.draw, width=card_copy.adjust_style)
    card_copy.bind(height=container.resize_v)
    container.add_widget(card_copy)

    card_copy.bind(height=lambda obj, height: adjust_pop_to_card(pop, height, screen_size[1]))
    card_copy.toggle_short_long()
    pop.open()


def adjust_pop_to_card(popup, height, screen_height):
    popup.height = height + dp(50) if height <= screen_height * 0.9 else screen_height * 0.9


def tags_popup(title: str, screen_size: tuple, database_dir: str, tag_callback, empty_title=None, not_names=None,
               names=None):
    # preparing tag popup
    tag_container = SmartGridLayout(cols=1, spacing=dp(10), size_hint=(1, None), padding=[0, dp(10)])
    slider = ScrollView(size=(screen_size[0] * 0.9, screen_size[1] * 0.5),
                        do_scroll_x=False, effect_y=ScrollEffect(), bar_inactive_color=(0, 0, 0, 0),
                        bar_color=(0, 0, 0, 0))

    workdir = Cache.get("app_info", "work_dir")

    slider.add_widget(tag_container)

    tags_pop = Popup(title=title, auto_dismiss=True,
                     size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 1),
                     title_color=get_color_from_hex("#444444"),
                     background=workdir + "/data/textures/popup_background.png",
                     title_size=screen_size[0] * 0.1 * 0.7, content=slider,
                     border=[0, 0, 0, 0])
    tags_pop.height += slider.height

    retrieved_tags = FlashcardDataBase.retrieve_tags(database_dir, not_names=not_names, names=names)

    if retrieved_tags:
        for index, tag in enumerate(retrieved_tags, 1):
            slider_tag = SliderTag(tag, index)
            slider_tag.bind(size=lambda obj, pos: obj.draw(), pos=lambda obj, pos: obj.adjust_style())
            slider_tag.bind(pos=lambda obj, pos: tag_container.resize_v(),
                            on_choose=tag_callback)
            slider_tag.bind(on_choose=lambda obj: tags_pop.dismiss())
            tag_container.add_widget(slider_tag)

    elif empty_title is not None:
        so_empty_lbl = Label(text=empty_title, size_hint=(1, None),
                             pos_hint={"center_y": 0.5, "center_x": 0.5},
                             color=get_color_from_hex("#444444"), font_size=screen_size[0] * 0.8 * 0.07)
        tags_popup.separator_color = (0, 0, 0, 1)
        tag_container.add_widget(so_empty_lbl)
        tags_pop.height -= slider.height - so_empty_lbl.height

    tag_container.resize_v()

    # if tag_container.height > slider.height:
    #     slider.do_scroll_y = True
    # else:
    #     slider.do_scroll_y = False
    slider.do_scroll_y = True

    return tags_pop


def boxes_popup(title: str, screen_size: tuple, database_dir: str, box_callback, empty_title=None,
                show_type: str = "all"):
    # preparing box popup
    box_container = SmartGridLayout(cols=2, spacing=dp(10), size_hint=(1, None), padding=[dp(5), dp(10)])
    slider = ScrollView(size=(screen_size[0] * 0.9, screen_size[1] * 0.5),
                        do_scroll_x=False, effect_y=ScrollEffect(), bar_inactive_color=(0, 0, 0, 0),
                        bar_color=(0, 0, 0, 0))

    workdir = Cache.get("app_info", "work_dir")

    slider.add_widget(box_container)

    box_pop = Popup(title=title, auto_dismiss=True,
                    size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 1),
                    title_color=get_color_from_hex("#444444"),
                    background=workdir + "/data/textures/popup_background_light.png",
                    title_size=screen_size[0] * 0.1 * 0.7, content=slider,
                    border=[0, 0, 0, 0])
    box_pop.height += slider.height

    retrieved_boxes = FlashcardDataBase.retrieve_boxes(database_dir)
    if show_type == "special":
        retrieved_boxes = [box for box in retrieved_boxes if box.is_special]

    elif show_type == "normal":
        retrieved_boxes = [box for box in retrieved_boxes if not box.is_special]

    if retrieved_boxes:
        for box in retrieved_boxes:
            slider_box = SliderBox(box)
            slider_box.bind(width=slider_box.adjust_style, size=slider_box.draw)
            slider_box.bind(pos=slider_box.draw, height=box_container.resize_v,
                            on_choose=box_callback)
            slider_box.bind(on_choose=lambda obj: box_pop.dismiss())
            box_container.add_widget(slider_box)

    elif empty_title is not None:
        so_empty_lbl = Label(text=empty_title, size_hint=(1, None),
                             pos_hint={"center_y": 0.5, "center_x": 0.5},
                             color=get_color_from_hex("#444444"), font_size=screen_size[0] * 0.7 * 0.07)
        tags_popup.separator_color = (0, 0, 0, 1)
        box_container.add_widget(so_empty_lbl)
        box_pop.height -= slider.height - so_empty_lbl.height

    if len(retrieved_boxes) == 1:
        box_container.add_widget(Label(opacity=0, size_hint=(0.45, None)))

    slider.do_scroll_y = True

    return box_pop


def revising_parameters_popup(screen_size: tuple, workdir, def_callback, submit_callback):
    layout = FloatLayout()

    def_btn = LanguageButton(size_hint=(0.45, None), pos_hint={"x": 0.03, "center_y": 0.7},
                             allow_no_selection=False, text="definition", group="show")
    hidden_btn = LanguageButton(size_hint=(0.45, None), pos_hint={"right": 0.97, "center_y": 0.7},
                                allow_no_selection=False,
                                text="hidden", group="show")

    submit_btn = MenuButton(size_hint=(0.7, None), pos_hint={"center_x": 0.5, "y": 0.04}, text="start revising")

    layout.add_widget(def_btn)
    layout.add_widget(hidden_btn)
    layout.add_widget(submit_btn)

    revising_pop = Popup(title="which side do you want to show first?", auto_dismiss=True,
                         size_hint=(0.9, None), title_align="center", separator_color=(0, 0, 0, 0),
                         title_color=get_color_from_hex("#444444"),
                         background=workdir + "/data/textures/popup_background.png",
                         title_size=screen_size[0] * 0.1 * 0.5, content=layout,
                         border=[0, 0, 0, 0], height=screen_size[0] * 0.6 + screen_size[0] * 0.1 * 0.5)

    def_btn.bind(state=def_callback)
    submit_btn.bind(on_release=submit_callback)
    submit_btn.bind(on_release=revising_pop.dismiss)

    def_btn.state = "down"

    return revising_pop
