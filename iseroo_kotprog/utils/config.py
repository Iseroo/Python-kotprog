import json


class Config:
    data = None
    images = None

    screen = None
    map_layer = None
    game_map = None
    all_characters = []

    items = {
        "FOOD": [],
        "WOOD": [],
        "STICK": [],
        "STONE": [],

    }

    cursor_style = None

    def set_cursor_style(style):
        if not style:
            Config.cursor_style = style
            return

    def load(path: str):
        with open(path, 'r') as f:
            Config.data = json.load(f)

    def load_image_locations(path: str):
        with open(path, 'r') as f:
            Config.images = json.load(f)

    def remove_from_items(type, item):

        Config.items[type].pop(Config.items[type].index(item))
