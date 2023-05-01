import json


class Config:
    data = {}
    images = {}

    screen = None
    map_layer = None
    game_map = None
    all_characters = []

    items = {
        "FOOD": [],
        "WOOD": [],
        "STICK": [],
        "STONE": [],
        "WOOD_SWORD": [],
        "STONE_SWROD": [],
        "PICKAXE": [],
        "AXE": [],
        "TORCH": [],


    }

    cursor_style = None

    @staticmethod
    def set_cursor_style(style):
        if not style:
            Config.cursor_style = style
            return

    @staticmethod
    def load(path: str):
        with open(path, 'r', encoding="UTF-8") as f:
            Config.data = json.load(f)

    @staticmethod
    def remove_from_items(item_type, item):

        Config.items[item_type].pop(Config.items[item_type].index(item))
