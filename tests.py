from PIL import Image as PIL_Image, ImageEnhance, ImageOps
from os import path

pil_img = PIL_Image.open("huge_image.png")
pil_img = ImageEnhance.Sharpness(pil_img).enhance(5)

huge_size = path.getsize("huge_image.png")
factor = huge_size / 1000000

pil_img = pil_img.reduce(int(factor))
# pil_img = pil_img.convert("L")
pil_img.save("small_image.png")
print(path.getsize("small_image.png"))