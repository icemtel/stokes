from PIL import Image


# Image.open() can also open other image types
img = Image.open("two_cilia.png")
width, height = img.size
width_new, height_new = width // 2, height //2
# WIDTH and HEIGHT are integers
resized_img = img.resize((width_new, height_new))
resized_img.save("two_cilia_new.png")