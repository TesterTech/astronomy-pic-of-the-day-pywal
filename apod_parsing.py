import json
import requests as req
import urllib.request
import urllib.parse
import os
from PIL import Image, ImageDraw, ImageFont

POD_SAVE_LOCATION = "~/Pictures/Wallpapers"

# if you don't select date it will use today's image of the day.
GET_APOD_URL = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY'
# GET_APOD_URL = 'https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date=2017-07-27'
# some test cases for the screen resolution
# date=2022-12-20' # Thor's Helmet (2048x1433)
# date=2022-12-19' # The Tadpole Nebula in Gas and Dust (2560x2048)


class Watermark:
    def __init__(self, cpyright=None, date=None, title=None, url=None):
        self.cpyright = cpyright
        self.date = date
        self.title = title
        self.url = url


class RunPywal:
    def __init__(self, image_name):
        os.system(f"$HOME/scripts/pywal.sh {image_name}")


def get_filename_from_image_metadata(url):
    parsed_url = urllib.parse.urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    return file_name


def parse_metadata_to_watermark(image_meta_data):
    if "copyright" in image_meta_data:
        watermark = Watermark(
            image_meta_data["copyright"],
            image_meta_data["date"],
            image_meta_data["title"],
            image_meta_data["url"],
        )
    else:  # ugly but sometimes no copyright key in Json and this revents error TODO: fix when empty metadata
        watermark = Watermark(
            "NASA",
            image_meta_data["date"],
            image_meta_data["title"],
            image_meta_data["url"],
        )
    return watermark


def save_the_image_to_disk(image_name, Watermark, save_location=POD_SAVE_LOCATION):
    img_data = req.get(Watermark.url).content
    with open(image_name, 'wb') as handler:
        watermark = f"Astronomy Picture of the Day (apod.nasa.gov)\n{Watermark.title} " \
                    f"[{Watermark.date}]\nCopyright: {Watermark.cpyright}\n"
        fill = (255, 0, 0)
        font_face = 'DejaVuSans'

        handler.write(img_data)
        img = Image.open(image_name)
        w, h = img.size
        print(f"Image width {w} and height {h}")
        I1 = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_face, int(h / 100))
        I1.text(
            (50, h - h / 5),
            watermark,
            font=font,
            fill=fill
        )
        # img.show()
        image_name = (f"{image_name}.jpg")
        img.save(fp=image_name, Path=save_location)
        print(f"The image {image_name} has been saved at {save_location}")
        return image_name


class PictureOfTheDay:
    image_meta_data = json.loads(req.get(GET_APOD_URL).text)
    Watermark = parse_metadata_to_watermark(image_meta_data)
    image_name = save_the_image_to_disk(Watermark.title.replace(" ", "-"), Watermark)
    RunPywal(image_name)


if __name__ == '__main__':
    PictureOfTheDay()
