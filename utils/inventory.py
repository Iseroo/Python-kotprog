

import random
import pygame
from utils.config import Config
from utils.functions import scale_image
from utils.item import Item
from utils.message_service import MessageService
from typing import *

from utils.text_display import TextDisplay


class Inventory:
    def __init__(self) -> None:
        self.slots: Dict[int, Item] = {x: None for x in range(10)}

    def add_item_to_stack(self, item: Item):
        for slot in self.slots:
            if self.slots[slot] is not None and self.slots[slot].type == item.type and self.slots[slot].count < self.slots[slot].max:
                self.slots[slot].count += item.count
                return True

        for slot in self.slots:
            if self.slots[slot] is None:
                self.slots[slot] = item
                return True

        MessageService.add(
            {'text': "Inventory is full", "severity": "warning"})

        return False

    def remove_item_from_slot(self, slot: int):
        removed_item = self.slots[slot]
        self.slots[slot] = None
        return removed_item


class InventoryHUD:
    def __init__(self, inventory: Inventory) -> None:
        self.inventory_offset = 12
        self.inv_bar = scale_image(
            pygame.image.load(Config.images["inventory_bar"]), 2)
        self.selected_slot_img = scale_image(pygame.image.load(
            Config.images["inventory_slot_selected"]), 2)

        self.inventory_Surface = pygame.Surface(
            (self.inv_bar.get_width(), self.inv_bar.get_height()))
        self.selected_slot = 0

        self.inventory = inventory
        self.update_slots()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.inventory_Surface, (screen.get_width() // 2 - self.inventory_Surface.get_width() // 2,
                                             screen.get_height() - self.inventory_Surface.get_height()))

    def select_slot(self, slot: int):
        if slot > 9:
            slot = 0
        elif slot < 0:
            slot = 9

        self.selected_slot = slot
        self.update_slots()

    def update_slots(self):
        self.inventory_Surface.blit(self.inv_bar, (0, 0))
        self.inventory_Surface.blit(
            self.selected_slot_img, (self.inventory_offset+((self.selected_slot_img.get_width() - 2) * (self.selected_slot)), self.inventory_offset))
        for item in self.inventory.slots:
            if self.inventory.slots[item] is not None:
                # print(self.inventory.slots[item].item_image)
                self.inventory_Surface.blit(self.inventory.slots[item].item_image, (
                    self.inventory_offset+((self.selected_slot_img.get_width() - 2) * (item)) + 4, self.inventory_offset + 4))

                text = TextDisplay(
                    str(self.inventory.slots[item].count), 12, (255, 255, 255))

                self.inventory_Surface.blit(text.draw(), (
                    self.inventory_offset+((self.selected_slot_img.get_width() - 2) * (item)) + 4, self.inventory_offset + 4))
