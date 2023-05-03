from enum import Enum

import pygame
from cat_royale.classes.config import Config
from cat_royale.classes.map_reader import get_map_sprite_image
from cat_royale.classes.message_service import MessageService


class MAPCOLOR(Enum):
    """Item enum

    colorcode of the items on the map
    """
    GRASS = '#32C832'
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
    MUSHROOM = (14, 12)
    APPLE = (14, 0)


def load_item_image(item_type: ITEM) -> pygame.Surface:
    """Loads the image of the item

    Args:
        item_type (ITEM): type of the item

    Returns:
        pygame.Surface: image of the item
    """
    sprite_sheet = pygame.image.load(
        Config.images["items"]).convert_alpha()

    return get_map_sprite_image(sprite_sheet, ITEM[item_type].value)


class Item:
    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1) -> None:
        self.count = 1
        self.max = stack_size
        self.item_image = item_image.copy()
        self.type = item_type

    def __str__(self) -> str:
        return self.type.name + " " + str(self.count)

    def use(self, *args):
        pass


class Food(Item):
    """ Food item class, child of Item class"""

    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1, hunger: int = 0, health: int = 0) -> None:
        super().__init__(item_image.copy(), item_type, stack_size)
        self.hunger = hunger
        self.health = health

    def use(self, character):
        """ Use function for food items, adds health and hunger to the character and removes the item from the inventory"""
        if self.count > 0:
            if character.player:
                MessageService.add(
                    {"text": "You ate the " + ITEM[self.type].name.lower() + ".", "severity": "info", "duration": 100})
            character.inventory.subtract_item(self.type, 1)
            character.inventory_hud.update_slots()
            character.add_hp(self.health)
            character.add_hunger(self.hunger)


class Weapon(Item):
    """ Weapon item class, child of Item class"""

    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1, damage: int = 0, durability: int = 0) -> None:
        super().__init__(item_image.copy(), item_type, stack_size)
        self.damage = damage
        self.durability = durability
        self.max_durability = durability

    def use(self, character):
        """ Use function for weapon items, deals damage to the character and lowers the durability of the item"""
        self.durability -= 1
        character.do_damage(self.damage)
        self.item_image.blit(self.make_durability_bar(),
                             (0, self.item_image.get_height() - 2))

    def make_durability_bar(self):
        """ Creates a durability bar for the weapon item"""
        durability_bar = pygame.Surface((self.item_image.get_width(), 2))
        durability_bar.fill((90, 0, 0))
        durability_bar.fill(
            (255, 0, 0), (0, 0, self.item_image.get_width() * self.durability / 100, 2))
        return durability_bar


class Material(Item):
    """ Material item class, child of Item class"""

    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1) -> None:
        super().__init__(item_image.copy(), item_type, stack_size)


class Tool(Item):
    """ Tool item class, child of Item class"""

    count = 0

    def __init__(self, item_image, item_type: ITEM = None, stack_size: int = 1, durability: int = 0) -> None:
        super().__init__(item_image.copy(), item_type, stack_size)
        self.durability = durability
        self.max_durability = durability
        Tool.count += 1
        self.id = Tool.count

    def use(self):
        """ Use function for tool items, and lowers the durability of the item"""
        self.durability -= 1
        self.item_image.blit(self.make_durability_bar(),
                             (0, self.item_image.get_height() - 2))

    def make_durability_bar(self):
        """ Creates a durability bar for the tool item"""
        durability_bar = pygame.Surface((self.item_image.get_width(), 2))
        durability_bar.fill((90, 0, 0))
        durability_bar.fill(
            (255, 0, 0), (0, 0, self.item_image.get_width() * (self.durability / self.max_durability), 2))
        return durability_bar
