"""
Astronomy Pic of the day downloader. All image rights belong to NASA!
This is just a wrapper for downloading the APOD from NASA
Script was made by Eric from TesterTech and is free to use.
Only request is to keep the link to my channel in this code.
https://github.com/testertech
https://youtube.com/@testertech
"""
import json
import urllib.request
import urllib.parse
import os
import shutil
import requests as req
from PIL import Image, ImageDraw, ImageFont

home = os.path.expanduser('~')

# Change to your preferred save location
POD_SAVE_LOCATION = f"{home}/Pictures/Wallpapers"
#
WATERMARK_FONT_FACE = 'DejaVuSans'
# if you don't select date it will use today's image of the day.
GET_APOD_URL = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'


# some test cases for the screen resolution
# date=2022-12-20' # Thor's Helmet (2048x1433)
# date=2022-12-19' # The Tadpole Nebula in Gas and Dust (2560x2048)
# GET_APOD_URL = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date=2023-03-23'


class Watermark:
    """
    Class for setting a watermark on the image from the metadata of the image
    """
    def __init__(self, cpyright=None, date=None, title=None, url=None):
        self.cpyright = cpyright
        self.date = date
        self.title = title
        self.url = url


class RunPywal:
    """Calling method for the script"""
    def __init__(self, image_name):
        send_dunst_message(f"Running Pywal on {image_name}")
        os.system(f"$HOME/scripts/pywal.sh {image_name}")


def get_filename_from_image_metadata(url):
    """
    parse image metadata to get the filename for saving
    """
    parsed_url = urllib.parse.urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    return file_name


def parse_metadata_to_watermark(image_meta_data):
    """
    Use the image metadata to get the values for the watermark
    """
    if "copyright" not in image_meta_data:
        # if the copyright element is missing, put NASA in there.
        image_meta_data["copyright"] = "NASA"
    watermark = Watermark(
        image_meta_data["copyright"],
        image_meta_data["date"],
        image_meta_data["title"],
        image_meta_data["url"],
    )
    return watermark


def save_the_image_to_disk(image_name, watermark, save_location=POD_SAVE_LOCATION):
    """
    This will write the image to local path (POD_SAVE_LOCATION)
    :param image_name:
    :param watermark:
    :param save_location:
    :return: None
    """
    image_name = f"{image_name}.jpg"
    full_save_path = f'{save_location}/{image_name}'
    if not os.path.exists(full_save_path):
        os.mkdir(full_save_path)
    img_data = req.get(watermark.url).content
    with open(image_name, 'wb') as handler:
        watermark = f"Astronomy Picture of the Day (apod.nasa.gov)\n{watermark.title} " \
                    f"[{watermark.date}]\nCopyright: {watermark.cpyright}\n"
        fill = (255, 0, 0)
        handler.write(img_data)
        img = Image.open(image_name)
        width, height = img.size
        print(f"Image width {width} and height {height}")
        the_image_to_draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(WATERMARK_FONT_FACE, int(height / 100))
        the_image_to_draw.text(
            (50, height - height / 5),
            watermark,
            font=font,
            fill=fill
        )
        img.save(full_save_path, 'JPEG')
        send_dunst_message(f"The image has been saved {image_name} at {save_location}")
        os.remove(image_name)
        return full_save_path


def send_dunst_message(message_text):
    """
    Dunst is used for sending notifications
    :param message_text:
    :return: None
    """
    print(f'>> {message_text}')
    if shutil.which('dunstify'):
        os.system(f"dunstify '{message_text}'")
    else:
        print('ERR: Program dunstify is not found, have you installed Dunst? ')


class PictureOfTheDay:
    """
    Main class to run the script.
    """
    image_meta_data = json.loads(req.get(GET_APOD_URL).text)
    media_type = image_meta_data["media_type"]
    if media_type != "image":
        print(f"Error Pic of the day is not image, it's {media_type}")
    else:
        Watermark = parse_metadata_to_watermark(image_meta_data)
        image_name = save_the_image_to_disk(
            Watermark.title.replace(" ", "-"), Watermark)
        RunPywal(image_name)


if __name__ == '__main__':
    PictureOfTheDay()
