import uuid

from PIL import Image
from io import BytesIO


def validate_file_type(filename: str, types):
    return filename != '' and \
        '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in types


def save_picture(file, path, crop=False):
    image_data = file.read()
    image = Image.open(BytesIO(image_data))

    if crop:
        width, height = image.size

        crop_reference = width if width < height else height
        crop_area = (0, 0, crop_reference, crop_reference)
        
        image = image.crop(crop_area)
        image = image.resize((480, 480), Image.ANTIALIAS)

    file_name = "%s.png" % str(uuid.uuid4())
    file_path = path + file_name

    image.save(file_path, format="png")

    return file_name


def save_file(file, path):
    file_name = "%s.pdf" % str(uuid.uuid4())
    file_path = path + file_name

    file.save(file_path)

    return file_name