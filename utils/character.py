from typing import *
from utils.functions import get_item_sprite_image, scale_sprites
from utils.inventory import Inventory
from utils.item import Item
import random
import pygame
from utils.config import Config


class Character:
    def __init__(self) -> None:
        self.sprites = {
            'walk': [],
            'died': [],
            'idle': [],

        }

        self.hp = 20
        self.max_hp = 100

        self.hunger = 0
        self.max_hunger = 100

        self.inventory = Inventory()

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

        self.tick_count = 0

    def tick(self):
        self. tick_count += 1
        if self.tick_count > 60:
            self.tick_count = 0

            if self.hunger <= 0:
                if self.hp > 0:
                    self.hp -= 1

    def load_sprite(self):
        img = pygame.image.load(Config.images["cat"]).convert_alpha()

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
        self.tick()
        if self.hp <= 0:
            self.died(screen)
            return

        self.wait_for_idle += 1

        if self.wait_for_idle >= 5:
            self.wait_for_idle = 100
            self.idle(screen)
        else:
            self.check_wall_boundries(screen)
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

    def check_wall_boundries(self, screen):
        if self.position[0] < 0:
            self.position = (0, self.position[1])
        elif self.position[0] > screen.get_width() - self.next_sprite.get_width():
            self.position = (screen.get_width() -
                             self.next_sprite.get_width(), self.position[1])

        if self.position[1] < 0:
            self.position = (self.position[0], 0)

    def get_position(self):
        return (self.position[0] + self.sprites['idle'][0].get_width() // 2, self.position[1] + self.sprites['idle'][0].get_height() // 2)

    def get_health(self):
        return (self.hp, self.hunger)
