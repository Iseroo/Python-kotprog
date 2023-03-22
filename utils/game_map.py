from utils.item import Item, MAPCOLOR
from typing import *
import pygame


class Block:
    size = 40

    def __init__(self, coords, type: MAPCOLOR) -> None:
        self.items: MutableSequence[Item] = []
        self.coords = coords
        self.type = type
        self.image = pygame.Surface((Block.size, Block.size))
        self.image.fill(self.type.rgb(self.type.value))

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)

    def set_image(self, type: MAPCOLOR):
        self.type = type
        self.image.fill(self.type.rgb(self.type.value))

    def draw(self, screen):
        screen.blit(self.image, self.coords)
        for item in self.items:
            screen.blit(item.item_image,
                        (self.coords[0] + 4, self.coords[1] + 4))


class GameMap:

    def __init__(self) -> None:
        self.blocks: MutableSequence[Block] = []

    def add_block(self, block: Block) -> None:
        self.blocks.append(block)

    def draw(self, screen):
        for block in self.blocks:
            block.draw(screen)
