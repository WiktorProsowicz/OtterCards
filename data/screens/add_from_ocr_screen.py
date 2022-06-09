from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.cache import Cache
from PIL import Image as PIL_Image, ImageEnhance, ImageOps
import ocrspace
from kivy.uix.image import Image
from kivy.clock import Clock
from ..classes.utils import ocr_language_map
from ..classes.language_button import LanguageButton
from kivy.app import App
from ..classes.cropping_rectangle import CroppingRectangle
from requests.exceptions import ConnectionError
from kivy.uix.camera import Camera
from ..classes.popups import ok_popup, loading_popup
from os import path


class AddFromOcrScreen(Screen):
    camera = ObjectProperty(None)
    camera_layout = ObjectProperty(None)
    refresh_btn = ObjectProperty(None)
    crop_btn = ObjectProperty(None)
    approve_btn = ObjectProperty(None)
    languages_dropdown = ObjectProperty(None)
    capture_btn = ObjectProperty(None)
    change_camera_btn = ObjectProperty(None)
    flip_v_btn = ObjectProperty(None)
    flip_h_btn = ObjectProperty(None)
    flip_right_btn = ObjectProperty(None)

    def change_camera(self):
        try:
            self.camera.index += 1

        except AttributeError:
            self.camera.index = 0

    def save_frame(self, *args):

        workdir = Cache.get("app_info", "work_dir")
        self.captured_image.texture.save(workdir + "/data/ocr_image.png", False)

        pil_img = PIL_Image.open(workdir + "/data/ocr_image.png")
        pil_img = ImageEnhance.Sharpness(pil_img).enhance(5)
        # pil_img = pil_img.convert("L")
        huge_size = path.getsize(workdir + "/data/ocr_image.png")
        
        factor = huge_size / 1000000
        pil_img = pil_img.reduce(int(factor))

        pil_img.save(workdir + "/data/ocr_image.png")

        loading_pop = loading_popup("scanning image...", self.width)
        loading_pop.open()

        Clock.schedule_once(lambda nt: self.convert_image(), .2)
        Clock.schedule_once(lambda nt: loading_pop.dismiss(), .2)

    def save_language(self, item, text):  # fired when language dropdown is selected
        self.selected_language = text

    def convert_image(self):
        workdir = Cache.get("app_info", "work_dir")
        try:
            with open(workdir + "/data/ocr_image.png", "rb") as f:
                api = ocrspace.API(api_key="K83095498688957", language=ocr_language_map()[self.selected_language])
                converted_text = api.ocr_file(f)

                Cache.append("card_chunks", "new_chunk", converted_text)
                App.get_running_app().switch_screen("card_chunks_screen", "inverted")

        except ConnectionError:

            warning_pop = ok_popup("something went wrong... check your connection and try again!", screen_width=self.width,
                                   btn_callback=lambda btn: App.get_running_app().switch_screen("previous", "inverted"))
            Cache.append("card_chunks", "new_chunk", "")
            warning_pop.open()

    def flip_captured_image(self, mode: str):
        imgdir = Cache.get("app_info", "work_dir") + "/data/captured_img.png"
        self.captured_image.texture.save(imgdir, False)

        if mode == "h":
            with PIL_Image.open(imgdir) as im:
                im = ImageOps.mirror(im)
                im.save(imgdir)
        elif mode == "v":
            with PIL_Image.open(imgdir) as im:
                im = ImageOps.flip(im)
                im.save(imgdir)

        elif mode == "right":
            with PIL_Image.open(imgdir) as im:
                im = im.rotate(-90, expand=True)
                im.save(imgdir)

        self.captured_image.reload()
        cw, ch = self.captured_image.get_norm_image_size()
        self.cropping_rect.reset((self.camera_layout.center_x - cw / 2, self.camera_layout.center_y - ch / 2), (cw, ch))

    def crop(self, *args):
        if self.cropping_rect not in self.camera_layout.children:  # returning original
            final_texture = self.captured_image.texture

        else:  # cropping texture
            tw, th = self.captured_image.texture_size[0], self.captured_image.texture_size[1]
            lw, lh = self.cropping_rect.drag_rect_width, self.cropping_rect.drag_rect_height

            x_pos = (self.cropping_rect.x - self.cropping_rect.drag_rect_x) * tw / lw
            y_pos = (self.cropping_rect.y - self.cropping_rect.drag_rect_y) * th / lh
            w, h = self.cropping_rect.width * tw / lw, self.cropping_rect.height * th / lh
            final_texture = self.captured_image.texture.get_region(x_pos, y_pos, w, h)

        self.captured_image.texture = final_texture
        self.camera_layout.remove_widget(self.cropping_rect)

        self.crop_btn.bind(on_release=self.start_cropping)
        self.crop_btn.unbind(on_release=self.crop)
        self.crop_btn.change_mode("enabled")

        self.camera_layout.remove_widget(self.flip_h_btn)
        self.camera_layout.remove_widget(self.flip_v_btn)
        self.camera_layout.remove_widget(self.flip_right_btn)

    def start_cropping(self, *args):
        self.camera_layout.add_widget(self.cropping_rect)

        self.crop_btn.unbind(on_release=self.start_cropping)
        self.crop_btn.bind(on_release=self.crop)
        self.crop_btn.change_mode("chosen")

        cw, ch = self.captured_image.get_norm_image_size()
        self.cropping_rect.reset((self.camera_layout.center_x - cw / 2, self.camera_layout.center_y - ch / 2), (cw, ch))

        self.camera_layout.add_widget(self.flip_h_btn, 0)
        self.camera_layout.add_widget(self.flip_v_btn, 0)
        self.camera_layout.add_widget(self.flip_right_btn, 0)

        dmtr = self.flip_v_btn.width / 2

        self.flip_h_btn.pos = (self.camera_layout.x + dmtr, self.camera_layout.y + dmtr)
        self.flip_v_btn.pos = (self.camera_layout.center_x - dmtr, self.camera_layout.y + dmtr)
        self.flip_right_btn.pos = (self.camera_layout.right - 3 * dmtr, self.camera_layout.y + dmtr)

    def capture(self):
        self.camera_layout.clear_widgets()
        self.camera.play = False

        workdir = Cache.get("app_info", "work_dir")
        self.camera.texture.save(workdir + "/data/captured_img.png", False)
        self.captured_image = Image(source=workdir + "/data/captured_img.png",
                                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                                    allow_stretch=True)
        self.camera_layout.add_widget(self.captured_image)
        self.captured_image.reload()

        self.crop_btn.bind(on_release=self.start_cropping)
        self.crop_btn.change_mode("enabled")
        self.refresh_btn.bind(on_release=self.refresh_camera)
        self.refresh_btn.change_mode("enabled")

        self.approve_btn.bind(on_release=self.save_frame)
        self.approve_btn.opacity = 1

    def refresh_camera(self, *args):

        if self.capture_btn not in self.camera_layout.children:
            self.camera_layout.add_widget(self.capture_btn)
            self.camera_layout.add_widget(self.camera)
            self.camera_layout.add_widget(self.change_camera_btn)

        self.camera_layout.remove_widget(self.cropping_rect)
        self.camera_layout.remove_widget(self.captured_image)

        self.camera.play = True

        self.crop_btn.unbind(on_release=self.start_cropping)
        self.crop_btn.change_mode("disabled")
        self.refresh_btn.unbind(on_release=self.refresh_camera)
        self.refresh_btn.change_mode("disabled")

        self.approve_btn.unbind(on_release=self.save_frame)
        self.approve_btn.opacity = 0.5

        self.camera_layout.remove_widget(self.flip_h_btn)
        self.camera_layout.remove_widget(self.flip_v_btn)
        self.camera_layout.remove_widget(self.flip_right_btn)

    def on_leave(self, *args):
        self.camera.play = False

    def on_pre_enter(self, *args):

        if self.cropping_rect is None:
            self.cropping_rect = CroppingRectangle()

        if self.camera is None:
            self.camera = Camera(pos_hint={"center_x": 0.5, "center_y": 0.5}, play=True)
            self.camera_layout.add_widget(self.camera)

        Clock.schedule_once(lambda nt: self.refresh_camera(), 0.05)
        self.languages_dropdown.bind(on_select=self.save_language)
        self.languages_dropdown.dismiss()

        if not self.languages_dropdown.container.children:
            for key in ocr_language_map().keys():
                btn = LanguageButton(allow_no_selection=False, group="languages")
                if key == "English":
                    btn.state = "down"
                btn.text = key
                btn.bind(on_release=lambda obj: self.languages_dropdown.select(obj.text))
                self.languages_dropdown.add_widget(btn)

    def __init__(self, **kwargs):
        super(AddFromOcrScreen, self).__init__(**kwargs)

        self.selected_language = "English"  # language selected by languages dropdown used for ocr scanning
        self.cropping_rect = None

        self.captured_image = Image()

