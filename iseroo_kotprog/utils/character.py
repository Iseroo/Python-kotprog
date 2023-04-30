import math
from typing import *
from utils.item import Weapon, Tool
from utils.inventory import InventoryHUD, CraftingHUD
from utils.message_service import MessageService
from utils.functions import get_item_sprite_image, scale_sprites
from utils.inventory import Inventory
import random
import pygame
from utils.config import Config


class Character:
    def __init__(self, player=True) -> None:
        self.player = player

        self.sprites = {
            'walk': [],
            'died': [],
            'idle': [],
            'doing': [],
            "attack": []

        }

        self.hp = 100
        self.max_hp = 100

        self.hunger = 100
        self.max_hunger = 100

        self.doing_percentage = 0

        self.inventory = Inventory()

        self.inventory_hud = InventoryHUD(self.inventory)
        self.inventory_hud.update_slots()

        self.crafting_hud = CraftingHUD(self)

        self.load_sprite()
        self.idle_generator = self.generate_idle()
        self.next_sprite = None
        self.wait_for_idle = 100

        self.walk_generator = self.generate_walk()
        self.walk_speed = 5

        self.die_generator = self.generate_died()
        self.died_speed = 10

        self.doing_generator = self.generate_doing()
        self.doingThing = False
        self.done = True
        self.doingTime = 100

        self.do_attack = False
        self.attack_generator = self.generate_attack()

        self.delay = Config.data["animation_delay"]
        self.current_time = 0

        self.position = (0, 0)

        self.tick_count = 0

        self.onblock = None

    def add_hp(self, hp):
        self.hp += hp if self.hp + hp < self.max_hp else self.max_hp - self.hp

    def add_hunger(self, hunger):
        self.hunger += hunger if self.hunger + \
            hunger < self.max_hunger else self.max_hunger - self.hunger

    def tick(self):
        self.tick_count += 1
        if self.tick_count > 60:
            self.tick_count = 0
            self.hunger += Config.data["hunger_per_tick"] if self.hunger > 0 else 0
            if self.hunger <= 0:
                if self.hp > 10:
                    self.hp += Config.data["health_if_hungry"]

    def add_event_to_craft_hud(self, event):
        self.crafting_hud.add_event_to_box(event)

    def load_sprite(self):
        cat_config = "cat_sprite_indexes" if self.player else "enemy_cat_sprite_indexes"
        img = pygame.image.load(
            Config.images["cat" if self.player else "enemy_cat"]).convert_alpha()

        walk = Config.data[cat_config]["walk"]
        self.sprites['walk'] = scale_sprites(get_item_sprite_image(
            img, walk["row"], walk["count"]), 1.5)

        died = Config.data[cat_config]["died"]
        self.sprites['died'] = scale_sprites(get_item_sprite_image(
            img, died['row'], died['count']), 1.5)

        idle = Config.data[cat_config]["idle"]
        self.sprites['idle'] = scale_sprites(get_item_sprite_image(
            img, idle['row'], idle['count']), 1.5)

        doing = Config.data[cat_config]["doing"]
        self.sprites['doing'] = scale_sprites(get_item_sprite_image(
            img, doing['row'], doing['count']), 1.5)

        attack = Config.data[cat_config]["attack"]
        self.sprites['attack'] = scale_sprites(get_item_sprite_image(
            img, attack['row'], attack['count']), 1.5)

    def add_item_to_inventory(self, item):
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

    def attack(self, screen):
        if self.next_sprite is None:
            self.next_sprite = next(self.attack_generator)

        if self.current_time < self.died_speed:
            self.current_time += 1
            screen.blit(self.next_sprite, self.position)
            return
        try:
            self.next_sprite = next(self.attack_generator)

        except StopIteration:
            self.attack_generator = self.generate_attack()
            self.next_sprite = next(self.attack_generator)
            self.do_attack = False

        screen.blit(self.next_sprite, self.position)
        self.current_time = 0

    def generate_attack(self):
        for sprite in self.sprites["attack"]:
            yield sprite

    def use_weapon_to_attack(self):
        selected_item = self.inventory.slots[self.inventory_hud.selected_slot]
        if not self.onblock:
            return

        coords = self.onblock.indexes
        to_be_checked = [(coords[0]-1, coords[1]-1), (coords[0]-1, coords[1]), (coords[0]-1, coords[1]+1), (coords[0], coords[1]-1),
                         (coords[0], coords[1]+1), (coords[0]+1, coords[1]-1), (coords[0]+1, coords[1]), (coords[0]+1, coords[1]+1), coords]
        characters_to_be_damaged = []
        for character in Config.all_characters:
            if character.get_index_coords() in to_be_checked:
                characters_to_be_damaged.append(character)
        if isinstance(selected_item, Weapon):
            for character in characters_to_be_damaged:
                if character != self:
                    selected_item.use(character)

            if selected_item.durability == 0:
                self.inventory.slots[self.inventory_hud.selected_slot] = None
        else:
            for character in characters_to_be_damaged:
                if character != self:
                    character.hp -= Config.data["damage"]['FIST']

    def do_damage(self, damage):
        self.hp -= damage if damage < self.hp else self.hp

    def get_index_coords(self):
        return self.onblock.indexes

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

    def generate_doing(self):
        for sprite in self.sprites["doing"]:
            yield sprite

    def doing(self, screen: pygame.Surface):
        if self.next_sprite is None:
            self.next_sprite = next(self.doing_generator)

        if self.current_time < self.delay:
            self.current_time += 1
            self.doing_percentage += 1
            if self.doing_percentage > self.next_sprite.get_width():
                self.doing_percentage = 0
            screen.blit(self.next_sprite, self.position)
            return
        try:
            self.next_sprite = next(self.doing_generator)

        except StopIteration:
            self.doing_generator = self.generate_doing()
            self.next_sprite = next(self.doing_generator)

        screen.blit(self.next_sprite, self.position)
        self.current_time = 0

    def doing_bar(self):
        bar = pygame.Surface((self.doing_percentage, 1))
        bar.fill((255, 255, 255))
        return bar

    def draw(self, screen: pygame.Surface):
        if self.onblock and len(self.onblock.items) > 0 and self.player:
            MessageService.add(
                {"text": "Press F to pickup", "severity": "info", "duration": 1})

        self.tick()
        if self.hp <= 0:
            self.died(screen)
            return

        self.wait_for_idle += 1

        if self.wait_for_idle >= 5:
            self.wait_for_idle = 100

            if self.doingThing and self.doingTime > 0:
                if self.done == False:
                    self.done = True
                self.doing(screen=screen)

                screen.blit(self.doing_bar(),
                            (self.position[0], self.position[1] + self.next_sprite.get_height()+10))
                self.doingTime -= 1

            elif self.do_attack:
                self.attack(screen)

            else:
                self.idle(screen)

        else:
            self.check_wall_boundries(screen)
            screen.blit(self.next_sprite, self.position)

        self.pickup_time()

    def move(self, direction):
        if self.hp <= 0:
            return
        if self.doingThing:
            return

        self.wait_for_idle = 0
        self.walk(direction)
        speed_modifier = 4
        if self.hp < 50 and self.hp >= 30:
            speed_modifier = 0.9
        elif self.hp < 30 and self.hp >= 10:
            speed_modifier = 0.75
        elif self.hp < 10:
            speed_modifier = 0.6

        if self.hunger < 50 and self.hunger >= 20:
            speed_modifier *= 0.9
        elif self.hunger < 20 and self.hunger > 0:
            speed_modifier *= 0.8
        elif self.hunger <= 0:
            speed_modifier *= 0.5

        if direction == 'left':
            self.position = (self.position[0] -
                             1*speed_modifier, self.position[1])
        elif direction == 'up':
            self.position = (self.position[0],
                             self.position[1] - 1*speed_modifier)
        elif direction == 'down':
            self.position = (self.position[0],
                             self.position[1] + 1*speed_modifier)
        elif direction == 'right':
            self.position = (self.position[0] +
                             1*speed_modifier, self.position[1])

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

    def set_onblock(self, block):
        self.onblock = block

    def pickup(self, map_layer):
        if self.onblock and len(self.onblock.items) > 0:
            if not self.check_necessary_item_for_pickup(self.onblock.items[-1].type):
                if self.player:
                    MessageService.add(
                        {'text': "Don't have necessary equipment!", "severity": "warning"})
                return False
            if self.inventory.isFull:
                if self.player:
                    MessageService.add(
                        {'text': "Inventory is full", "severity": "warning"})
                return False
            self.doingThing = True
            try:
                self.doingTime = Config.data["item_pickup_time"][self.onblock.items[0].type]
            except:
                self.doingTime = 1

        return False

    def check_necessary_item_for_pickup(self, pickup):

        if pickup in Config.data["necessary_items_for_pickup"]:
            necessary = Config.data["necessary_items_for_pickup"][pickup]
            for (key, item) in self.inventory.slots.items():
                if item and item.type == necessary:
                    item.use()

                    if isinstance(item, Weapon) or isinstance(item, Tool) and item.durability <= 0:
                        self.inventory.slots[key] = None
                    return True
            return False
        return True

    def use_slot(self):
        if self.inventory.slots[self.inventory_hud.selected_slot]:
            self.inventory.slots[self.inventory_hud.selected_slot].use(self)

    def pickup_time(self):
        if not self.done:
            return
        elif self.done and self.doingTime <= 0:
            picked_up = self.onblock.remove_item_from_top()
            if picked_up:
                self.inventory.add_item_to_stack(picked_up)
                self.onblock.draw(Config.map_layer)
                self.inventory_hud.update_slots()
            self.done = False
            self.doingThing = False
            self.doingTime = 0
            self.doing_percentage = 0


class Enemy(Character):
    def __init__(self) -> None:
        super().__init__(player=False)
        self.todo_stack = []
        self.wait = 10
        self.picking = False

    def ai(self, map_layer, other_characters=None, near_objects=None):
        if self.hp <= 0:
            return
        if not self.onblock:
            return
        coords = self.onblock.indexes
        to_be_checked = [coords, (coords[0]-1, coords[1]-1), (coords[0]-1, coords[1]), (coords[0]-1, coords[1]+1), (coords[0], coords[1]-1),
                         (coords[0], coords[1]+1), (coords[0]+1, coords[1] -
                                                    1), (coords[0]+1, coords[1]), (coords[0]+1, coords[1]+1),
                         (coords[0]-2), (coords[1]-2), (coords[0]-2, coords[1]-1), (coords[0] -
                                                                                    2, coords[1]), (coords[0]-2, coords[1]+1), (coords[0]-2, coords[1]+2),
                         (coords[0]-1, coords[1]-2), (coords[0]-1, coords[1]+2), (coords[0], coords[1] -
                                                                                  2), (coords[0], coords[1]+2), (coords[0]+1, coords[1]-2), (coords[0]+1, coords[1]+2),
                         (coords[0]+2, coords[1]-2), (coords[0]+2, coords[1]-1), (coords[0]+2, coords[1]), (coords[0]+2, coords[1]+1), (coords[0]+2, coords[1]+2)]
        characters_to_be_damaged = []
        for character in Config.all_characters:
            if character.get_index_coords() in to_be_checked:
                characters_to_be_damaged.append(character)

        if len(characters_to_be_damaged) > 1:
            has_alive = [
                character for character in characters_to_be_damaged if character.hp > 0]
            if len(has_alive) > 0:
                if self.wait <= 0:
                    for character in characters_to_be_damaged:
                        if character != self and character.hp > 0:
                            self.auto_move_to_pos(character.position)
                            self.do_attack = True
                            self.use_weapon_to_attack()
                    self.wait = 10
                else:
                    self.wait -= 1
                return
        if self.hunger < 30:
            closest_food = None
            closest_distance = 100000
            for food in Config.items['FOOD']:
                if food.type == "MUSHROOM":
                    return
                food_distance = math.sqrt(
                    (food.coords[0]-self.position[0])**2 + (food.coords[1]-self.position[1])**2)
                if food_distance < closest_distance:
                    closest_distance = food_distance
                    closest_food = food
            if closest_food:
                self.auto_move_to_pos(closest_food.coords)
                if closest_distance < 2:
                    self.pickup(map_layer)

                    self.eat()

    def eat(self):
        if self.inventory.slots[0]:
            self.inventory.slots[0].use(self)

    def get_inventory(self):
        return self.inventory

    def auto_move_to_pos(self, pos):
        if self.hp <= 0:
            return

        if self.position[0] < pos[0]:
            self.move('right')
        elif self.position[0] > pos[0]:
            self.move('left')
        if self.position[1] < pos[1]:
            self.move('down')
        if self.position[1] > pos[1]:
            self.move('up')

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(self.next_sprite, (90, 0, 0), (0, self.next_sprite.get_height(
        )-2, self.next_sprite.get_width(), 2))
        pygame.draw.rect(self.next_sprite, (255, 0, 0), (0, self.next_sprite.get_height(
        )-2, self.next_sprite.get_width()*(self.hp/100), 2))
