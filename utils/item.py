from enum import Enum
from utils.character import Character
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
        
class Food(Item):
    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1, hunger: int = 0, health: int = 0) -> None:
        super().__init__(item_image, item_type, stack_size)
        self.hunger = hunger
        self.health = health

    def use(self, character: Character):
        if self.count > 0: 
            MessageService.add({"text": "You ate the " + self.type.name.lower() + ".", "severity": "info", "duration": 100})
            self.count -= 1
            character.hp += self.health
            character.hunger += self.hunger
        
class Weapon(Item):
    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1, damage: int = 0, durability: int = 0) -> None:
        super().__init__(item_image, item_type, stack_size)
        self.damage = damage
        self.durability = durability

    def use(self, character: Character):
        MessageService.add({"text": "You used the " + self.type.name.lower() + ".", "severity": "info", "duration": 100})
        self.durability -= 1
        character.hp -= self.damage
        
        
class Material(Item):
    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1) -> None:
        super().__init__(item_image, item_type, stack_size)

    def use(self):
        MessageService.add({"text": "You used the " + self.type.name.lower() + ".", "severity": "info", "duration": 100})
        self.count -= 1

class Tool(Item):
    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1, durability: int = 0) -> None:
        super().__init__(item_image, item_type, stack_size)
        self.durability = durability

    def use(self):
        MessageService.add({"text": "You used the " + self.type.name.lower() + ".", "severity": "info", "duration": 100})
        self.durability -= 1