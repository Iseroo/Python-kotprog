import json


class Config:
    data = None
    images = None

    def load(path: str):
        with open(path, 'r') as f:
            Config.data = json.load(f)

    def load_image_locations(path: str):
        with open(path, 'r') as f:
            Config.images = json.load(f)
