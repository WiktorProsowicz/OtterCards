from kivy.uix.screenmanager import Screen
from kivy.cache import Cache
from kivy.app import App
from ..classes.slider_chunk import SliderChunk
from kivy.properties import ObjectProperty
from ..classes.dismissable_bubble import DismissableBubble, DismissableBubbleButton
from data.flashcards.flashcard_database import FlashcardDataBase, Flashcard, LengthError
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from ..classes.popups import ok_popup


class CardChunksScreen(Screen):
    slider_container = ObjectProperty(None)
    slider = ObjectProperty(None)
    bubble_layout = ObjectProperty(None)

    def discard(self):
        self.slider_chunks.clear()
        App.get_running_app().switch_screen("add_cards_screen", "right")

    def save(self):
        def_lines, hidden_lines = [], []
        for chunk in self.slider_chunks:
            if chunk.hidden:
                hidden_lines.append(chunk.text)
            else:
                def_lines.append(chunk.text)

        database_f = Cache.get("app_info", "database_dir")
        try:
            FlashcardDataBase.insert_cards(database_f, [Flashcard(id=None, hidden_lines=hidden_lines, def_lines=def_lines)])

        except LengthError:
            warning_pop = ok_popup("some of the lines have invalid length!", self.width)
            warning_pop.open()

        else:
            self.slider_chunks.clear()
            App.get_running_app().switch_screen("add_cards_screen", "right")

    def add_chunk(self):
        App.get_running_app().switch_screen("add_from_ocr_screen", "inverted")

    def delete_chunks(self, *args):
        marked_chunks = [chunk for chunk in self.slider_chunks if chunk.marked]
        for chunk in marked_chunks:
            self.slider_chunks.remove(chunk)

        self.refresh()

    def swap_chunks(self, chunk):
        marked_chunks = [chunk for chunk in self.slider_chunks if chunk.marked]
        for chunk in marked_chunks:
            chunk.toggle_hidden()
            chunk.toggle_marked()

    def shift_chunk(self, chunk, direction: str):
        el_index = self.slider_chunks.index(chunk)
        self.slider_chunks.remove(chunk)
        if direction == "down":
            self.slider_chunks.insert(el_index + 1, chunk)
            # if self.slider.do_scroll_y:
            #     self.slider.scroll_y -= self.slider_chunks[el_index].height / self.slider.height
            #     if self.slider.scroll_y < 0:
            #         self.slider.scroll_y = 0

        elif el_index == 0:
            self.slider_chunks.insert(el_index, chunk)

        else:
            self.slider_chunks.insert(el_index - 1, chunk)

            # if self.slider.do_scroll_y:
            #     self.slider.scroll_y += self.slider_chunks[el_index].height / self.slider.height
            #     if self.slider.scroll_y > 1:
            #         self.slider.scroll_y = 1

        self.refresh()
        Clock.schedule_once(self.show_bubble, .025)

    def merge_chunks(self, *args):
        marked_chunks = [chunk for chunk in self.slider_chunks if chunk.marked]

        for chunk in marked_chunks[1:]:
            marked_chunks[0].text += " " + chunk.text
            self.slider_chunks.remove(chunk)

        marked_chunks[0].adjust_style()
        marked_chunks[0].draw()
        marked_chunks[0].toggle_marked()

        self.refresh()

    def break_chunk(self, chunk):

        el_index = self.slider_chunks.index(chunk)
        texts = []

        while len(texts) < 2:
            if "\n" in chunk.text:
                texts = chunk.text.split("\n")
            elif "." in chunk.text:
                texts = chunk.text.split(".")
            elif " " in chunk.text:
                texts = chunk.text.split(" ")
            else:
                chunk.adjust_style()
                chunk.toggle_marked()
                return None

            while "" in texts:
                texts.remove("")

            while " " in texts:
                texts.remove(" ")

            if len(texts) == 1:
                chunk.text = texts[0]

            elif len(texts) == 0:
                self.slider_chunks.remove(chunk)
                return None

        self.slider_chunks.remove(chunk)
        for index, text in enumerate(texts, el_index):
            slider_chunk = SliderChunk(text, chunk.hidden)
            self.slider_chunks.insert(index, slider_chunk)

        self.refresh()

    def show_bubble(self, *args):
        marked_chunks = [chunk for chunk in self.slider_chunks if chunk.marked]

        if len(marked_chunks) == 0:
            if self.bubble_layout.children:
                self.bubble_layout.children[0].dismiss()

        else:
            chunk = None
            for marked_chunk in marked_chunks:
                chunk_top = marked_chunk.to_window(0, marked_chunk.top)[1]
                chunk_y = marked_chunk.to_window(0, marked_chunk.y)[1]

                if chunk_top < self.slider.y or chunk_y > self.slider.top:
                    continue

                elif chunk_top > self.slider.top and chunk_y < self.slider.y:
                    continue

                else:
                    chunk = marked_chunk
                    break

            if chunk is None:
                if self.bubble_layout.children:
                    self.bubble_layout.children[0].dismiss()
                return None

            height = self.bubble_layout.width * 0.17
            width = self.bubble_layout.width * 0.33 if len(marked_chunks) > 1 else self.bubble_layout.width * 0.55
            chunk_top = chunk.to_window(0, chunk.top)[1]
            chunk_y = chunk.to_window(0, chunk.y)[1]
            chunk_center_x = chunk.to_window(chunk.center_x, 0)[0]

            if self.slider.top - chunk_top > chunk_top - self.slider.y:
                if chunk_center_x < self.slider.center_x:
                    pos = chunk.to_window(chunk.x, chunk.top)
                    arrow_pos = "bottom_left"
                else:
                    pos = chunk.to_window(chunk.right - width, chunk.top)
                    arrow_pos = "bottom_right"

            elif self.slider.top - chunk_y < chunk_y - self.slider.y:
                if chunk_center_x < self.slider.center_x:
                    pos = chunk.to_window(chunk.x, chunk.y - height)
                    arrow_pos = "top_left"
                else:
                    pos = chunk.to_window(chunk.right - width, chunk.y - height)
                    arrow_pos = "top_right"

            else:
                if chunk_center_x < self.slider.center_x:
                    pos = chunk.to_window(chunk.x, chunk.top)
                    arrow_pos = "bottom_left"
                else:
                    pos = chunk.to_window(chunk.right - width, chunk.top)
                    arrow_pos = "bottom_right"

            if not self.bubble_layout.children:
                workdir = Cache.get("app_info", "work_dir")
                bubble = DismissableBubble(self.bubble_layout, pos=pos, border=[0, 0, 0, 0], size_hint=(None, None),
                                           arrow_pos=arrow_pos, size=(width, height),
                                           background_image=workdir + "/data/textures/bubble_background.png")

                if len(marked_chunks) == 1:
                    del_btn = DismissableBubbleButton(workdir + "/data/textures/delete_icon.png")
                    swap_btn = DismissableBubbleButton(workdir + "/data/textures/swap_icon.png")
                    up_btn = DismissableBubbleButton(workdir + "/data/textures/up_icon.png", "square")
                    down_btn = DismissableBubbleButton(workdir + "/data/textures/down_icon.png", "square")
                    break_btn = DismissableBubbleButton(workdir + "/data/textures/break_icon.png")

                    lay = BoxLayout(orientation="vertical")
                    lay.add_widget(up_btn)
                    lay.add_widget(down_btn)

                    bubble.add_widget(del_btn)
                    bubble.add_widget(swap_btn)
                    bubble.add_widget(break_btn)
                    bubble.add_widget(lay)

                    del_btn.bind(on_release=bubble.dismiss)
                    del_btn.bind(on_release=self.delete_chunks)
                    swap_btn.bind(on_release=bubble.dismiss)
                    swap_btn.bind(on_release=self.swap_chunks)
                    down_btn.bind(on_release=lambda btn: self.shift_chunk(chunk, "down"))
                    up_btn.bind(on_release=lambda btn: self.shift_chunk(chunk, "up"))
                    break_btn.bind(on_release=bubble.dismiss)
                    break_btn.bind(on_release=lambda btn: self.break_chunk(chunk))

                else:
                    del_btn = DismissableBubbleButton(workdir + "/data/textures/delete_icon.png")
                    merge_btn = DismissableBubbleButton(workdir + "/data/textures/merge_icon.png")
                    swap_btn = DismissableBubbleButton(workdir + "/data/textures/swap_icon.png")

                    bubble.add_widget(del_btn)
                    bubble.add_widget(merge_btn)
                    bubble.add_widget(swap_btn)

                    del_btn.bind(on_release=bubble.dismiss)
                    del_btn.bind(on_release=self.delete_chunks)
                    merge_btn.bind(on_release=bubble.dismiss)
                    merge_btn.bind(on_release=self.merge_chunks)
                    swap_btn.bind(on_release=bubble.dismiss)
                    swap_btn.bind(on_release=self.swap_chunks)

                bubble.show()

            else:
                if len(self.bubble_layout.children[0].content.children) == 4 and len(marked_chunks) > 1 \
                        or len(self.bubble_layout.children[0].content.children) == 3 and len(marked_chunks) == 1:
                    self.bubble_layout.clear_widgets()
                    return self.show_bubble()

                self.bubble_layout.children[0].pos = pos
                self.bubble_layout.children[0].arrow_pos = arrow_pos

    def refresh(self):
        self.slider_container.clear_widgets()
        for chunk in self.slider_chunks:
            chunk.bind(pos=chunk.adjust_style)
            chunk.bind(size=chunk.draw, pos=chunk.draw)

            chunk.bind(marked=self.show_bubble)
            chunk.bind(on_hold=chunk.toggle_marked)

            chunk.bind(pos=self.slider_container.resize_v)
            self.slider_container.add_widget(chunk)

        self.slider_container.bind(height=self.enable_scroll)
        self.slider_container.bind(pos=self.show_bubble)
        self.slider_container.resize_v()

        self.slider.bind(on_scroll_stop=self.show_bubble)
        # self.slider.bind(on_scroll_start=self.show_bubble)
        self.slider.bind(scroll_y=self.show_bubble)

    def enable_scroll(self, *args):
        if self.slider_container.height > self.slider.height:
            self.slider.do_scroll_y = True
        else:
            self.slider.do_scroll_y = False

    def on_leave(self, *args):
        self.slider_container.clear_widgets()
        for chunk in self.slider_chunks:
            if chunk.marked:
                chunk.toggle_marked()

    def on_enter(self, *args):
        new_chunk = Cache.get("card_chunks", "new_chunk")
        if new_chunk != "":
            self.slider_chunks.append(SliderChunk(new_chunk, True))

        self.refresh()
        self.slider.scroll_y = 1

    def __init__(self, **kwargs):
        super(CardChunksScreen, self).__init__(**kwargs)

        self.slider_chunks = []  # list of widgets displayed in main scroll view
