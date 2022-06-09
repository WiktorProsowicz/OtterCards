from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, ListProperty
from kivy.utils import get_color_from_hex
from data.flashcards.flashcard_database import FlashcardDataBase, Tag
from kivy.cache import Cache
from kivy.app import App
from kivy.metrics import dp
from ..classes.utensils import UtensilDropUp, UtensilButton
from ..classes.slider_tag import SliderTag
from kivy.uix.label import Label
from kivy.clock import Clock


class TagsCollectionScreen(Screen):
    slider_container = ObjectProperty(None)
    slider_tags = ListProperty([])
    slider = ObjectProperty(None)
    more_btn = ObjectProperty(None)
    utensils = ObjectProperty(None)
    title_label = ObjectProperty(None)
    main_layout = ObjectProperty(None)

    def send_to_workshop(self, tag_item):
        if not hasattr(tag_item, "tag"):
            base_tag = Tag(None, "new tag", "c8c8c8")
        else:
            base_tag = Tag(tag_item.tag.id, tag_item.tag.name, tag_item.tag.color)

        Cache.append("tag_workshop", "base_tag", base_tag)
        app = App.get_running_app()
        app.switch_screen("tag_workshop_screen", "up")

    def choose_tag(self, tag_item):
        if tag_item.index == 0:
            Cache.append("cards_collection", "main_filter", "all")
        else:
            Cache.append("cards_collection", "main_filter", tag_item.tag.name)

        App.get_running_app().switch_screen("cards_collection_screen", "left")

    def delete_tags(self, title_label):
        database_f = Cache.get("app_info", "database_dir")
        to_remove = []
        for tag in self.slider_tags:
            if tag.to_delete:
                FlashcardDataBase.delete_tag(database_f, tag.tag)
                to_remove.append(tag)

        if not to_remove:
            return False

        for tag in to_remove:
            self.slider_tags.remove(tag)

        if self.delete_mode:
            self.toggle_delete_mode(None)

        self.slider_container.clear_widgets()
        self.refresh()
        self.utensils.toggle(self.more_btn, mode="open")

    def toggle_delete_mode(self, delete_btn):

        if self.edit_mode:
            self.toggle_edit_mode(None)

        self.delete_mode = not self.delete_mode

        if self.delete_mode:
            self.utensils.toggle(None, mode="close")  # option buttons disappear after choosing one of them

            for child in self.slider_container.children:
                child.unbind(on_choose=self.choose_tag)
                if child.index != 0:
                    child.opacity = 0.5
                    child.bind(on_choose=child.toggle_delete)

            self.title_label.text = "click to delete"
            self.title_label.bind(on_release=self.delete_tags)
            self.title_label.toggle_mode("deleting")

            self.utensils.items["delete_btn"].change_mode("chosen")

        else:
            for child in self.slider_container.children:
                child.unbind(on_choose=child.toggle_delete)
                child.bind(on_choose=self.choose_tag)
                if child.to_delete:
                    child.toggle_delete(None)
                child.opacity = 1

            self.title_label.text = "tags & cards"
            self.title_label.unbind(on_release=self.delete_tags)
            self.title_label.toggle_mode("normal")

            self.utensils.items["delete_btn"].change_mode("enabled")

    def toggle_edit_mode(self, edit_btn):
        if self.delete_mode:
            self.toggle_delete_mode(None)

        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            self.utensils.toggle(None, mode="close")  # option buttons disappear after choosing one of them

            self.title_label.text = "choose to edit"

            for child in self.slider_container.children:
                child.unbind(on_choose=self.choose_tag)
                if child.index != 0:
                    child.bind(on_choose=self.send_to_workshop)

            self.utensils.items["edit_btn"].change_mode("chosen")

        else:
            self.title_label.text = "tags & cards"

            for child in self.slider_container.children:
                child.bind(on_choose=self.choose_tag)
                if child.index != 0:
                    child.unbind(on_choose=self.send_to_workshop)

            self.utensils.items["edit_btn"].change_mode("enabled")

    def refresh(self):
        # initial filling the slider container layout
        for tag in self.slider_tags:
            self.slider_container.add_widget(tag)
            tag.bind(size=tag.draw, pos=self.slider_container.resize_v)
            tag.bind(on_choose=self.choose_tag, pos=tag.adjust_style)

        self.slider_container.resize_v()

        # adding encouraging label in case there are no tags
        if len(self.slider_tags) == 1 and self.so_empty_lbl not in self.main_layout.children:

            self.so_empty_lbl = Label(text="so empty...\nconsider adding some tags!", size_hint=(1, None),
                                      pos_hint={"center_y": 0.7, "center_x": 0.5},
                                      color=get_color_from_hex("#AAAAAA"), font_size=self.slider_container.width * 0.07)

            self.main_layout.add_widget(self.so_empty_lbl)

        elif len(self.slider_tags) > 1 and self.so_empty_lbl in self.main_layout.children:
            self.main_layout.remove_widget(self.so_empty_lbl)

        # the user can scroll only when there is some content out of his sight
        # self.slider.do_scroll_y = False if self.slider_container.height < self.slider.height else True

        if self.utensils is not None:
            self.update_buttons()

        self.slider.scroll_y = 1

    def on_leave(self, *args):
        self.slider_container.clear_widgets()
        self.slider_tags.clear()

        if self.delete_mode:
            self.toggle_delete_mode(None)

        if self.edit_mode:
            self.toggle_edit_mode(None)

        self.utensils.toggle(None, mode="close")

    def on_pre_enter(self, *args):

        # preparing all tags
        database_f = Cache.get("app_info", "database_dir")

        first_tag = Tag(0, "all cards", "AAAAAA")
        num_of_all_cards = FlashcardDataBase.number_cards_in_tag(database_f, first_tag)
        self.slider_tags = [SliderTag(first_tag, 0, num_of_all_cards)]

        retrieved_tags = FlashcardDataBase.retrieve_tags(database_f)
        retrieved_tags.sort(key=lambda tag: tag.last_update, reverse=True)
        
        for tag_index, tag in enumerate(retrieved_tags, 1):
            num_cards = FlashcardDataBase.number_cards_in_tag(database_f, tag)
            self.slider_tags.append(SliderTag(tag, tag_index, num_cards))

        Clock.schedule_once(lambda nt: self.refresh(), 0.05)

    def on_enter(self, *args):
        if self.utensils is None:
            self.utensils = UtensilDropUp(pos=(self.more_btn.x, -dp(10)))

            # preparing action buttons
            work_dir = Cache.get("app_info", "work_dir") + "/data/textures"
            delete_btn = UtensilButton(work_dir + "/delete_icon.png", work_dir + "/delete_icon_chosen.png",
                                       height=self.more_btn.height, width=self.more_btn.width)
            edit_btn = UtensilButton(work_dir + "/edit_icon.png", work_dir + "/edit_icon_chosen.png",
                                     height=self.more_btn.height, width=self.more_btn.width)
            add_btn = UtensilButton(work_dir + "/add_icon.png",
                                    height=self.more_btn.height, width=self.more_btn.width)

            delete_btn.bind(pos=delete_btn.draw)
            edit_btn.bind(pos=edit_btn.draw)
            add_btn.bind(pos=add_btn.draw, on_release=self.send_to_workshop)

            self.utensils.items["delete_btn"] = delete_btn
            self.utensils.items["edit_btn"] = edit_btn
            self.utensils.items["label_btn"] = add_btn

            self.more_btn.bind(on_release=self.utensils.toggle)

            self.ids["additional_layout"].add_widget(self.utensils)

        self.update_buttons()
        # self.refresh()

    def update_buttons(self):

        # buttons actions and appearance based on number of tags
        if len(self.slider_tags) > 1:
            self.utensils.items["delete_btn"].bind(on_release=self.toggle_delete_mode)
            self.utensils.items["delete_btn"].change_mode("enabled")
            self.utensils.items["edit_btn"].bind(on_release=self.toggle_edit_mode)
            self.utensils.items["edit_btn"].change_mode("enabled")

        else:
            self.utensils.items["delete_btn"].unbind(on_release=self.toggle_delete_mode)
            self.utensils.items["delete_btn"].change_mode("disabled")
            self.utensils.items["edit_btn"].unbind(on_release=self.toggle_edit_mode)
            self.utensils.items["edit_btn"].change_mode("disabled")

    def __init__(self, **kwargs):
        super(TagsCollectionScreen, self).__init__(**kwargs)
        self.delete_mode = False
        self.edit_mode = False
        self.utensils = None
        self.so_empty_lbl = None
