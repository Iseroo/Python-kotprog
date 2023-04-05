from enum import Enum
from utils.message_service import MessageService


class MAPCOLOR(Enum):
    """Item enum

    colorcode of the items on the map
    """
    GRASS = '#32C832'
    WATER = "#3264C8"
    WOOD = "#C86432"
    STONE = "#C8C8C8"
    STICK = "#F0B478"
    BERRY = "#FF0000"
    CARROT = "#FAC800"

    def rgb(self, hexa) -> tuple:
        """Converts a hexa colorcode to a rgb tuple

        Args:
            hexa (str): hexa colorcode

        Returns:
            tuple: rgb tuple
        """
        hexa = int(hexa[1:], 16)
        return ((hexa >> 16) & 0xFF, (hexa >> 8) & 0xFF, hexa & 0xFF)


class ITEM(Enum):
    """Item position on sprite sheet

    type of the items
    """
    WOOD = (17, 0)
    CARROT = (14, 6)
    BERRY = (14, 4)
    STICK = (12, 2)
    STONE = (17, 1)
    AXE = (4, 6)
    PICKAXE = (4, 5)
    TORCH = (10, 10)
    WOOD_SWORD = (5, 0)
    STONE_SWORD = (5, 1)
    FIREPIT = (4, 2)
    MUSHROOM = (14, 12)
    APPLE = (14, 0)


class Item:
    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1) -> None:
        self.count = 1
        self.max = stack_size
        self.item_image = item_image
        self.type = item_type
