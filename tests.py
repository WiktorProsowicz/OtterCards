from PIL import Image, ImageEnhance, ImageFilter
import ocrspace
from data.classes.utils import hex_to_hsl, hsl_to_hex
# im = Image.open("data/tests/ocr_image_.png")
# im = ImageEnhance.Sharpness(im).enhance(7)
# im = im.convert("L")
# # im = ImageEnhance.Contrast(im).enhance(1)
# # im = im.filter(ImageFilter.MinFilter(3))
#
# im.save("data/tests/ocr_image -- kopia.png")
#
# api = ocrspace.API(api_key="K83095498688957", language=ocrspace.Language.Polish)
# with open("data/tests/ocr_image -- kopia.png", "rb") as f:
#     print(api.ocr_file(f))

def random_words():
    word = ""
    for i in range(randint(20, 40)):
        char = " " if randint(0, 100) > 80 else chr(randint(40, 90))
        word += char
    return "Super Idol的笑容 都没你的甜 八月正午的阳"

from data.flashcards.flashcard_database import FlashcardDataBase, Box
from kivy.utils import get_random_color, get_hex_from_color
# from random import randint
#
# database_f = "data/sample_database.db"
# print(database_f)

# for i in range(1):
#     r, g, b, a = get_random_color()
#     hex = get_hex_from_color((r, g, b)).lstrip("#")
#     box = Box(id=None, nr_compartments=randint(5, 10), is_special=bool(randint(0, 2)),
#               name=random_words(), color=hex)
#     FlashcardDataBase.insert_box(database_f, box)

# lista = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
# sett = set(lista)
# lista = list(sett)
# print(lista, sett)

# print(",".join(["?"] * 0))

from data.classes.utils import a_difference_b
print(a_difference_b([], [1, 2, 3, 4]))