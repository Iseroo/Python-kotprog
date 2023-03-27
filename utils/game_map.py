from utils.item import Item, MAPCOLOR
from typing import *
import pygame
import random
from utils.map_reader import get_map_sprite_image
from utils.message_service import MessageService


class Block:
    size = 40

    def __init__(self, coords, type: MAPCOLOR) -> None:
        self.items: MutableSequence[Item] = []
        self.coords = coords
        self.type = type
        self.image = pygame.Surface((Block.size, Block.size))
        self.display_text = ""
        self.reset_block_image()

    def reset_block_image(self):
        if self.type != MAPCOLOR.WATER:
            self.image.fill(MAPCOLOR.GRASS.rgb(MAPCOLOR.GRASS.value))
            self.image.blit(get_map_sprite_image(
                pygame.image.load('assets/images/grass.png').convert_alpha(), (random.randint(0, 4), random.randint(0, 4))), (4, 4))
        else:
            self.image.fill(MAPCOLOR.WATER.rgb(MAPCOLOR.WATER.value))

    def add_item(self, item: Item) -> None:
        self.items.append(item)

        self.set_item_image()

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)
        self.set_item_image()

    def remove_item_from_top(self) -> None:
        if len(self.items) > 0:
            removed_item = self.items.pop()
            self.set_item_image()
            return removed_item

    def set_item_image(self):
        self.reset_block_image()
        for item in self.items:
            self.image.blit(item.item_image, (4, 4))

    def draw(self, screen):

        self.set_item_image()
        screen.blit(self.image, self.coords)

    def on_block_check(self, coords, screen=None):

        if self.coords[0] <= coords[0] <= self.coords[0] + Block.size and self.coords[1] <= coords[1] <= self.coords[1] + Block.size:
            if len(self.items) > 0:
                MessageService.add(
                    {"text": "Press F to pickup", "severity": "info", "duration": 1})
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

    def on_block_check(self, coords, screen=None) -> Block:
        for block in self.blocks:
            item = block.on_block_check(coords, screen=screen)
            if item is not None:
                # print("on block")
                return item
        return None
