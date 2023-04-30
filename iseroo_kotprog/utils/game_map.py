from utils.item import Item, MAPCOLOR
from typing import *
import pygame
import random
from utils.map_reader import get_map_sprite_image
from utils.message_service import MessageService
from utils.config import Config


class Block:
    size = 40

    def __init__(self, coords, type: MAPCOLOR) -> None:

        self.items: MutableSequence[Item] = []
        self.coords = coords
        self.indexes = self.calc_indexes()
        self.type = type
        self.image = pygame.Surface((Block.size, Block.size))
        self.display_text = ""
        self.reset_block_image()

    def calc_indexes(self):
        return (self.coords[0] // Block.size, self.coords[1] // Block.size)

    def reset_block_image(self):

        self.image.fill(MAPCOLOR.GRASS.rgb(MAPCOLOR.GRASS.value))
        self.image.blit(get_map_sprite_image(
            pygame.image.load('assets/images/grass.png').convert_alpha(), (random.randint(0, 4), random.randint(0, 4))), (4, 4))

    def add_item(self, item: Item) -> None:
        self.items.append(item)

        item_type = ""
        match item.type:
            case "BERRY" | "MUSHROOM" | "APPLE" | "CARROT":
                item_type = "FOOD"
            case _:
                item_type = item.type

        Config.items[item_type].append(self)

        self.set_item_image()

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)
        self.set_item_image()

    def remove_item_from_top(self) -> None:
        if len(self.items) > 0:
            removed_item = self.items.pop()
            self.set_item_image()

            item_type = ""
            match removed_item.type:
                case "BERRY" | "MUSHROOM" | "APPLE" | "CARROT":
                    item_type = "FOOD"
                case _:
                    item_type = removed_item.type

            Config.remove_from_items(item_type, self)
            return removed_item

    def set_item_image(self):
        self.reset_block_image()
        for item in self.items:
            self.image.blit(item.item_image, (4, 4))

    def draw(self, screen):

        self.set_item_image()
        screen.blit(self.image, self.coords)

    def mouse_on_block(self, camera_pos):
        if len(self.items) == 0:
            return False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + abs(camera_pos[0]),
                     mouse_pos[1] + abs(camera_pos[1]))
        if self.coords[0] <= mouse_pos[0] <= self.coords[0] + Block.size and self.coords[1] <= mouse_pos[1] <= self.coords[1] + Block.size:
            return True
        return False

    def on_block_check(self, coords, screen=None):

        if self.coords[0] <= coords[0] <= self.coords[0] + Block.size and self.coords[1] <= coords[1] <= self.coords[1] + Block.size:
            return self

        return None


class GameMap:

    def __init__(self) -> None:
        self.blocks: MutableSequence[Block] = []

    def add_block(self, block: Block) -> None:
        self.blocks.append(block)

    def draw(self, screen):
        for block in self.blocks:
            block.draw(screen)

    def on_block_check(self, coords, screen=None, camera_pos=(0, 0)) -> Block:
        index_x, remainging_x = coords[0] // Block.size, coords[0] % Block.size
        index_y, remainging_y = coords[1] // Block.size, coords[1] % Block.size
        block = self.blocks[int(index_x*100+index_y)]

        if block:
            block.mouse_on_block(camera_pos)
            item = block.on_block_check(coords, screen=screen)
            if item is not None:
                return item
        return None

    def get_block_by_coords(self, coords) -> Block:
        for block in self.blocks:
            if block.coords[0] <= coords[0] <= block.coords[0] + Block.size and block.coords[1] <= coords[1] <= block.coords[1] + Block.size:
                return block
        return None

    def get_block_by_indexes(self, indexes) -> Block:
        for block in self.blocks:
            if block.indexes == indexes:
                return block
        return None
