

import random
import pygame
from utils.item import Weapon, Tool, Food, Material
from utils.event_stack import Event, EventStack, WindowStack
from utils.box import Box
from utils.config import Config
from utils.functions import scale_image
from utils.message_service import MessageService
from typing import *
from utils.item import load_item_image, Item

from utils.text_display import TextDisplay


class Inventory:
    def __init__(self) -> None:
        self.slots = {x: None for x in range(10)}
        self.isFull = False

    def __str__(self) -> str:
        return str(self.slots)

    def add_item_to_stack(self, item):
        for slot in self.slots:
            if self.slots[slot] is not None and self.slots[slot].type == item.type and self.slots[slot].count < self.slots[slot].max:
                self.slots[slot].count += item.count
                self.isFull = self.checkFull()
                return True

        for slot in self.slots:
            if self.slots[slot] is None:
                self.slots[slot] = item
                self.isFull = self.checkFull()
                return True

        return False

    def checkFull(self):
        for slot in self.slots:
            if self.slots[slot] is None:
                return False

            elif self.slots[slot].count < self.slots[slot].max:
                return False

        return True

    def subtract_item(self, item, count):
        for slot in self.slots:
            if self.slots[slot] is not None and self.slots[slot].type == item:
                self.slots[slot].count -= count
                if self.slots[slot].count <= 0:
                    self.slots[slot] = None
                return True
        return False

    def remove_item_from_slot(self, slot: int):
        removed_item = self.slots[slot]
        self.slots[slot] = None
        return removed_item

    def use_item(self, slot: int):
        if self.slots[slot] is not None:
            self.slots[slot].use()
            if self.slots[slot].count <= 0:
                self.slots[slot] = None
           
            return True
        return False


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


class CraftingHUD:
    def __init__(self, player) -> None:
        self.inventory_offset = 12
        self.inventory_offsetx = 8
        self.opened = False

        self.box = Box((500, 300), parent=self)
        self.box.position = (Config.screen.get_width() // 2 - self.box.Surface.get_width() // 2,
                             Config.screen.get_height() // 2 - self.box.Surface.get_height() // 2)

        self.player = player
        self.inventory = player.inventory

        self.slot_img = scale_image(pygame.image.load(
            Config.images["inventory_slot"]), 2)

        self.slots = {x: self.slot_img.copy() for x in range(9)}
        self.result = self.slot_img.copy()
        self.arrow = pygame.image.load(Config.images["arrow"])
        self.inv_bar = scale_image(pygame.image.load(
            Config.images["inventory_bar"]), 2)

        self.hud_surface = pygame.Surface(
            (self.slot_img.get_width() * 6, self.slot_img.get_height() * 3), pygame.SRCALPHA)

        self.craftable_items = Config.data["craft_items"]
        self.craftable_items_img = {
            x: load_item_image(x) for x in self.craftable_items}
        self.ingredients = {x: [(y, Config.data["craft_items"][x][y]) for y in Config.data["craft_items"][x]]
                            for x in self.craftable_items}

        self.craftable_items_hud = self.inv_bar.copy()

        self.selected_slot_img = scale_image(pygame.image.load(
            Config.images["inventory_slot_selected"]), 2)

        self.to_craft = None

        self.callback = None

        self.update()
        self.update_craftable_items()

    def add_event_to_box(self, event):
        self.box.set_close_event(event)

    def empty_slots(self):
        self.slots = {x: self.slot_img.copy() for x in range(9)}
        self.result = self.slot_img.copy()

    def toggle(self):
        self.box.opened = not self.box.opened
        self.update_craftable_items()
        self.update()

    def draw(self, screen: pygame.Surface):
        self.box.position = (screen.get_width() // 2 - self.box.size[0] // 2,
                             screen.get_height()//2 - self.box.size[1]//2)

        self.box.opened = True

        screen.blit(self.hud_surface, (screen.get_width() // 2 - self.hud_surface.get_width() // 2,
                                       screen.get_height()//2 - self.hud_surface.get_height()//2))

        screen.blit(self.craftable_items_hud, (screen.get_width() // 2 - self.craftable_items_hud.get_width() // 2,
                                               screen.get_height()//2 - self.craftable_items_hud.get_height()//2 - 100))
        self.mouse_on_item(pygame.mouse.get_pos(), screen)
        self.craft(screen)

    def update(self):
        # draw slots in 3x3 grid with 0px spacing

        for slot in self.slots:
            self.hud_surface.blit(
                self.slots[slot], (slot % 3 * self.slot_img.get_width(), slot // 3 * self.slot_img.get_height()))

        self.hud_surface.blit(
            self.result, (self.slot_img.get_width() * 5, self.slot_img.get_height()))

        self.hud_surface.blit(

            self.arrow, (int(self.slot_img.get_width() * 3.1), self.slot_img.get_height()))

        self.box.reset_and_add(self.hud_surface, (self.box.size[0] // 2 - self.hud_surface.get_width() // 2,
                                                  self.box.size[1] // 2 - self.hud_surface.get_height() // 2))
        self.box.add_element(self.craftable_items_hud, (self.box.size[0] // 2 - self.craftable_items_hud.get_width() // 2,
                                                        self.box.size[1] // 2 - self.craftable_items_hud.get_height() // 2 - 100))

    def update_craftable_items(self):
        self.craftable_items_hud = self.inv_bar.copy()
        for item in self.craftable_items:
            self.craftable_items_hud.blit(self.craftable_items_img[item], (self.inventory_offset + 4 + (
                (self.craftable_items_img[item].get_width() - 2 + self.inventory_offsetx) * ([*self.craftable_items.keys()].index(item))), self.inventory_offset + 4))

    def mouse_on_item(self, mouse_pos, screen):
        # set mouse_pos (0,0) as the craftable_items_hud position (0,0)
        mouse_pos = (mouse_pos[0] - (screen.get_width() // 2 - self.box.Surface.get_width() // 2 + (self.box.size[0] // 2 - self.craftable_items_hud.get_width() // 2)),
                     mouse_pos[1] - (screen.get_height()//2 - self.box.Surface.get_height()//2 + (self.box.size[1] // 2 - self.craftable_items_hud.get_height() // 2 - 100)))
        for item in self.craftable_items:
            self.update_craftable_items()
            item_coords = (self.inventory_offset + 4 + (
                (self.craftable_items_img[item].get_width() - 2 + self.inventory_offsetx) * ([*self.craftable_items.keys()].index(item))), self.inventory_offset + 4)
            if mouse_pos[0] >= item_coords[0] and mouse_pos[0] <= item_coords[0] + self.craftable_items_img[item].get_width() and mouse_pos[1] >= item_coords[1] and mouse_pos[1] <= item_coords[1] + self.craftable_items_img[item].get_height():
                self.craftable_items_hud.blit(self.selected_slot_img, (self.inventory_offset + (
                    (self.craftable_items_img[item].get_width() - 2 + self.inventory_offsetx) * ([*self.craftable_items.keys()].index(item))), self.inventory_offset))
                Config.set_cursor_style(pygame.SYSTEM_CURSOR_HAND)

                self.update()
                if pygame.mouse.get_pressed()[0]:
                    self.empty_slots()
                    self.to_craft = None

                    self.set_crafint_table(item)
                return
        self.update_craftable_items()

    def set_crafint_table(self, item):

        for index, ingredient in enumerate(self.ingredients[item]):
            self.slots[index].blit(load_item_image(ingredient[0]), (4, 4))
            text = TextDisplay(
                str(ingredient[1]), 12, (255, 255, 255))
            self.slots[index].blit(text.draw(), (4, 4))

        self.to_craft = item
        self.result.blit(self.craftable_items_img[item], (4, 4))

        self.update()

    def craft(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] - (screen.get_width() // 2 - self.hud_surface.get_width() // 2),
                     mouse_pos[1] - (screen.get_height()//2 - self.hud_surface.get_height()//2))

        if mouse_pos[0] >= self.slot_img.get_width() * 5 and mouse_pos[0] <= self.slot_img.get_width() * 5 + self.slot_img.get_width() and mouse_pos[1] >= self.slot_img.get_height() and mouse_pos[1] <= self.slot_img.get_height() + self.slot_img.get_height():
            # mouse pointer
            Config.cursor_style = pygame.SYSTEM_CURSOR_HAND
            if pygame.mouse.get_pressed()[0]:
                if self.to_craft != None:
                    for ingredient in self.ingredients[self.to_craft]:
                        found = False
                        for item_index in self.inventory.slots:

                            if self.inventory.slots[item_index] and self.inventory.slots[item_index].type == ingredient[0]:
                                found = True
                                if self.inventory.slots[item_index].count < ingredient[1]:
                                    return
                        if not found:
                            return

                    for ingredient in self.ingredients[self.to_craft]:
                        # for item_index in self.inventory.slots:
                        self.inventory.subtract_item(
                            ingredient[0], ingredient[1])
                    item_type = Config.data['item_types'][self.to_craft]

                    match item_type:
                        case 'Weapon':
                            try:
                                damage = Config.data["damage"][self.to_craft]
                            except KeyError:
                                damage = 3
                            self.inventory.add_item_to_stack(Weapon(
                                self.craftable_items_img[self.to_craft], self.to_craft, Config.data['items_stack_size'][self.to_craft], damage=damage, durability=Config.data["durabilities"][self.to_craft]))

                        case 'Tool':
                            self.inventory.add_item_to_stack(Tool(
                                self.craftable_items_img[self.to_craft], self.to_craft, Config.data['items_stack_size'][self.to_craft], Config.data["durabilities"][self.to_craft]))
                        case 'Food':
                            self.inventory.add_item_to_stack(Food(
                                self.craftable_items_img[self.to_craft], self.to_craft, Config.data['items_stack_size'][self.to_craft], Config.data["food_health_bonus"][self.to_craft][0], Config.data["food_health_bonus"][self.to_craft][1]))
                        case 'Material':
                            self.inventory.add_item_to_stack(Material(
                                self.craftable_items_img[self.to_craft], self.to_craft, Config.data['items_stack_size'][self.to_craft]))
                    # if self.inventory.slots[item_index] and self.inventory.slots[item_index].type == ingredient[0]:
                    #     self.inventory.slots[item_index].count -= ingredient[1]

                    self.empty_slots()
                    self.player.inventory_hud.update_slots()
                    self.to_craft = None
                    self.update()
                    self.update_craftable_items()
                    return

    @property
    def Surface(self):
        self.update_craftable_items()
        self.mouse_on_item(pygame.mouse.get_pos(), Config.screen)
        self.craft(Config.screen)

        self.box()

        return self.box
