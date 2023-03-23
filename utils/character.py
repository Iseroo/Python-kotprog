from typing import *
from utils.item import Item
import random
import pygame
from utils.config import Config


def get_item_sprite_image(sprite_sheet: pygame.Surface, row_index: int, count: int, sprite_size=32, spacing: int = 0):

    sprites = [pygame.Surface(
        (sprite_size, sprite_size), pygame.SRCALPHA) for x in range(count)]

    for i in range(count):

        sprites[i].blit(sprite_sheet, (0, 0), (i * (sprite_size + spacing), row_index * (sprite_size + spacing),
                                               sprite_size, sprite_size))

    return sprites


def scale_sprites(sprites: list, scale: float):
    return [pygame.transform.scale(x, (x.get_width() * scale, x.get_height() * scale)) for x in sprites]


class Character:
    def __init__(self) -> None:
        self.sprites = {
            'walk': [],
            'died': [],
            'idle': [],

        }

        self.hp = 100
        self.max_hp = 100

        self.inventory = {
            x: None for x in range(5)
        }

        self.load_sprite()
        self.idle_generator = self.generate_idle()
        self.next_sprite = None
        self.wait_for_idle = 100  # max 100

        self.walk_generator = self.generate_walk()
        self.walk_speed = 5

        self.die_generator = self.generate_died()
        self.died_speed = 10

        self.delay = Config.data["animation_delay"]
        self.current_time = 0

        self.position = (0, 0)

    def load_sprite(self):
        img = pygame.image.load('assets/images/cat.png').convert_alpha()

        walk = Config.data["cat_sprite_indexes"]["walk"]
        self.sprites['walk'] = scale_sprites(get_item_sprite_image(
            img, walk["row"], walk["count"]), 1.5)

        died = Config.data["cat_sprite_indexes"]["died"]
        self.sprites['died'] = scale_sprites(get_item_sprite_image(
            img, died['row'], died['count']), 1.5)

        idle = Config.data["cat_sprite_indexes"]["idle"]
        self.sprites['idle'] = scale_sprites(get_item_sprite_image(
            img, idle['row'], idle['count']), 1.5)

    def add_item_to_inventory(self, item: Item):
        for slot in self.inventory:
            if self.inventory[slot] is None:
                self.inventory[slot] = {'item': item, 'count': 1}
                break

    def generate_walk(self):
        for sprite in self.sprites["walk"]:
            yield sprite

    def walk(self, direction):
        if self.current_time < self.walk_speed:
            self.current_time += 1
            return
        try:
            self.next_sprite = next(self.walk_generator)

        except StopIteration:
            self.walk_generator = self.generate_walk()
            self.next_sprite = next(self.walk_generator)
        if direction == 'left':
            self.next_sprite = pygame.transform.flip(
                self.next_sprite, True, False)
        self.current_time = 0

    def died(self, screen):
        if self.next_sprite is None:
            self.next_sprite = next(self.die_generator)

        if self.current_time < self.died_speed:
            self.current_time += 1
            screen.blit(self.next_sprite, self.position)
            return
        try:
            self.next_sprite = next(self.die_generator)

        except StopIteration:
            self.die_generator = self.generate_died()
            self.next_sprite = next(self.die_generator)

        screen.blit(self.next_sprite, self.position)
        self.current_time = 0

    def generate_died(self):
        for sprite in self.sprites["died"]:
            yield sprite

    def generate_idle(self):
        for sprite in self.sprites["idle"]:
            yield sprite

    def idle(self, screen):
        if self.next_sprite is None:
            self.next_sprite = next(self.idle_generator)

        if self.current_time < self.delay:
            self.current_time += 1
            screen.blit(self.next_sprite, self.position)
            return
        try:
            self.next_sprite = next(self.idle_generator)

        except StopIteration:
            self.idle_generator = self.generate_idle()
            self.next_sprite = next(self.idle_generator)

        screen.blit(self.next_sprite, self.position)
        self.current_time = 0

    def draw(self, screen):
        if self.hp <= 0:
            self.died(screen)
            return

        self.wait_for_idle += 1

        if self.wait_for_idle >= 5:
            self.wait_for_idle = 100
            self.idle(screen)
        else:
            screen.blit(self.next_sprite, self.position)

    def move(self, direction):
        if self.hp <= 0:
            return

        self.wait_for_idle = 0
        self.walk(direction)
        if direction == 'left':
            self.position = (self.position[0] - 1, self.position[1])
        elif direction == 'right':
            self.position = (self.position[0] + 1, self.position[1])
        elif direction == 'up':
            self.position = (self.position[0], self.position[1] - 1)
        elif direction == 'down':
            self.position = (self.position[0], self.position[1] + 1)
