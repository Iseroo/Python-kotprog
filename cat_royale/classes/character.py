import math
import pygame
from cat_royale.classes.item import Weapon, Tool
from cat_royale.classes.inventory import InventoryHUD, CraftingHUD
from cat_royale.classes.message_service import MessageService
from cat_royale.classes.functions import get_item_sprite_image, scale_sprites
from cat_royale.classes.inventory import Inventory
from cat_royale.classes.config import Config


class Character:
    """
    The Character class represents a character in the game, either the player or an enemy.

    Attributes:
        player (bool): True if the character is a player, False if it's an enemy.\n
        sprites (dict): Dictionary containing lists of sprites for different actions.\n
        hp (int): Health points of the character.\n
        max_hp (int): Maximum health points a character can have.\n
        hunger (int): Hunger points of the character.\n
        max_hunger (int): Maximum hunger points a character can have.\n
        doing_percentage (int): The percentage of progress made in doing an action.\n
        inventory (Inventory): The character's inventory.\n
        inventory_hud (InventoryHUD): The HUD (Heads Up Display) for the character's inventory.\n
        crafting_hud (CraftingHUD): The HUD for the character's crafting.\n
        idle_generator (generator): Generator for the idle sprites.\n
        next_sprite (pygame.Surface): The next sprite to be drawn for the character.\n
        wait_for_idle (int): Time to wait before returning to idle.\n
        walk_generator (generator): Generator for the walking sprites.\n
        walk_speed (int): Speed of the character animation when walking.\n
        die_generator (generator): Generator for the dying sprites.\n
        died_speed (int): Speed of the character when dying.\n
        doing_generator (generator): Generator for the doing action sprites.\n
        doingThing (bool): Whether the character is doing an action.\n
        done (bool): Whether the character has finished doing an action.\n
        doingTime (int): Time taken to do an action.\n
        do_attack (bool): Whether the character is performing an attack.\n
        attack_generator (generator): Generator for the attack sprites.\n
        delay (int): Delay in sprite animation.\n
        current_time (int): Current time in the game.\n
        position (tuple): The current position of the character on the screen.\n
        tick_count (int): The count of ticks in the game.\n
        onblock (Block): The block the character is currently on.\n
    """

    def __init__(self, player=True) -> None:
        """
        Constructs all the necessary attributes for the character object.

        Args:
            player (bool): True if the character is a player, False if it's an enemy. Defaults to True.
        """
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
        """
        Adds a specified amount of health points (hp) to the character, without exceeding the maximum HP.
        """
        self.hp += hp if self.hp + hp < self.max_hp else self.max_hp - self.hp

    def add_hunger(self, hunger):
        """
        Adds a specified amount of hunger points to the character, without exceeding the maximum hunger.
        """
        self.hunger += hunger if self.hunger + \
            hunger < self.max_hunger else self.max_hunger - self.hunger

    def tick(self):
        """
        Handles the tick event for the character, which updates the hunger and HP values over time.
        """
        self.tick_count += 1
        if self.tick_count > 60:
            self.tick_count = 0
            self.hunger += Config.data["hunger_per_tick"] if self.hunger > 0 else 0
            if self.hunger <= 0:
                if self.hp > 10:
                    self.hp += Config.data["health_if_hungry"]

    def add_event_to_craft_hud(self, event):
        """
        Adds an event to the crafting HUD's event box.
        """
        self.crafting_hud.add_event_to_box(event)

    def load_sprite(self):
        """
        Loads the sprite images for the character from the configuration data.
        """
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

    def generate_walk(self):
        """
        A generator that iterates through the character's walking sprites.
        """
        for sprite in self.sprites["walk"]:
            yield sprite

    def walk(self, direction):
        """
        Updates the character's sprite and position based on the given direction ('left', 'right', 'up', 'down').
        """
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
        """
        Handles the character's death by updating the sprite and displaying it on the screen.
        """
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
        """
        A generator that iterates through the character's dying sprites.
        """
        for sprite in self.sprites["died"]:
            yield sprite

    def attack(self, screen):
        """
        Handles the character's attack by updating the sprite and displaying it on the screen.
        """
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
        """
        A generator that iterates through the character's attack sprites.
        """
        for sprite in self.sprites["attack"]:
            yield sprite

    def use_weapon_to_attack(self):
        """
        Uses the selected weapon in the inventory to attack nearby characters.
        """
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
        """
        Reduces the character's HP by the specified amount of damage.
        """
        self.hp -= damage if damage < self.hp else self.hp

    def get_index_coords(self):
        """
        Returns the index coordinates of the block the character is currently on.
        """
        return self.onblock.indexes

    def generate_idle(self):
        """
        A generator that iterates through the character's idle sprites.
        """
        for sprite in self.sprites["idle"]:
            yield sprite

    def idle(self, screen):
        """
        Updates the character's sprite to an idle state and displays it on the screen.
        """
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
        """
        A generator that iterates through the character's 'doing' (action) sprites.
        """
        for sprite in self.sprites["doing"]:
            yield sprite

    def doing(self, screen: pygame.Surface):
        """
        Updates the character's sprite to a 'doing' (action) state and displays it on the screen.
        """
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
        """
        Returns a pygame Surface representing the progress bar for the character's current action.
        """
        bar_surface = pygame.Surface((self.doing_percentage, 1))
        bar_surface.fill((255, 255, 255))
        return bar_surface

    def draw(self, screen: pygame.Surface):
        """
        Draws the character's current sprite on the screen, handling different states and actions.
        """
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
                if not self.done:
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
        """
        Moves the character in the specified direction ('left', 'right', 'up', 'down'), taking into account the character's HP and hunger.
        """
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
        """
        Ensures the character does not move beyond the screen boundaries.
        """
        if self.position[0] < 0:
            self.position = (0, self.position[1])
        elif self.position[0] > screen.get_width() - self.next_sprite.get_width():

            self.position = (screen.get_width() -
                             self.next_sprite.get_width(), self.position[1])

        if self.position[1] < 0:
            self.position = (self.position[0], 0)

    def get_position(self):
        """
        Returns the current position of the character as a tuple (x, y).
        """
        return (self.position[0] + self.sprites['idle'][0].get_width() // 2, self.position[1] + self.sprites['idle'][0].get_height() // 2)

    def get_health(self):
        """
        Returns the character's current health points (HP, Hunger) as an integer.
        """
        return (self.hp, self.hunger)

    def set_onblock(self, block):
        """
        Sets the character's current block, updating the character's position to be centered on the specified block.
        """
        self.onblock = block

    def pickup(self):
        """
        Attempt to pick up an item from the block the character is standing on.

        Returns:
            bool: False if the item could not be picked up, True otherwise.
        """
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
            except KeyError:
                self.doingTime = 1

        return False

    def check_necessary_item_for_pickup(self, pickup):
        """
        Checks if the character has the necessary item in their inventory to pick up the specified item.

        Returns True if the necessary item is found, otherwise False.
        """

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
        """
        Selects the specified inventory slot (slot_number) for use. If an item is in the selected slot, the character will use it.
        """
        if self.inventory.slots[self.inventory_hud.selected_slot]:
            self.inventory.slots[self.inventory_hud.selected_slot].use(self)

    def pickup_time(self):
        """
        Picks up an item from the block the character is standing on,
        if the character is currently picking up an item, and the necessary time has passed.
        """
        if not self.done:
            return
        if self.done and self.doingTime <= 0:
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
    """
    Enemy class represents an enemy character in the game, derived from the Character class.
    """

    def __init__(self) -> None:
        """
        Initializes an instance of the Enemy class with specific attributes and calls the superclass constructor.
        """
        super().__init__(player=False)
        self.wait = 10
        self.picking = False

    def ai(self):
        """
        Controls the artificial intelligence of the enemy, including movement, attacking, and eating behaviors.

        Args:
            map_layer: The game's map layer.

        """
        if self.hp <= 0:
            return
        if not self.onblock:
            return
        coords = self.onblock.indexes
        to_be_checked = [coords,
                         (coords[0] - 1, coords[1] - 1),
                         (coords[0] - 1, coords[1]),
                         (coords[0] - 1, coords[1] + 1),
                         (coords[0], coords[1] - 1),
                         (coords[0], coords[1] + 1),
                         (coords[0] + 1, coords[1] - 1),
                         (coords[0] + 1, coords[1]),
                         (coords[0] + 1, coords[1] + 1),
                         (coords[0] - 2), (coords[1] - 2),
                         (coords[0] - 2, coords[1] - 1),
                         (coords[0] - 2, coords[1]),
                         (coords[0] - 2, coords[1] + 1),
                         (coords[0] - 2, coords[1] + 2),
                         (coords[0] - 1, coords[1] - 2),
                         (coords[0] - 1, coords[1] + 2),
                         (coords[0], coords[1] - 2),
                         (coords[0], coords[1] + 2),
                         (coords[0] + 1, coords[1] - 2),
                         (coords[0] + 1, coords[1] + 2),
                         (coords[0] + 2, coords[1] - 2),
                         (coords[0] + 2, coords[1] - 1),
                         (coords[0] + 2, coords[1]),
                         (coords[0] + 2, coords[1] + 1),
                         (coords[0] + 2, coords[1] + 2)]  # 5x5 area around the character
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
            self.search_food()

    def search_food(self):
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
                self.pickup()

                self.eat()

    def eat(self):
        """
        Makes the enemy eat an item from its inventory to restore hunger.
        """
        if self.inventory.slots[0]:
            self.inventory.slots[0].use(self)

    def auto_move_to_pos(self, pos):
        """
        Automatically moves the enemy towards the specified position.

        Args:
            pos: A tuple representing the target position (x, y).
        """
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
        """
        Draws the enemy's current sprite on the screen, including the health bar.

        Args:
            screen: A pygame.Surface representing the game screen.
        """
        super().draw(screen)
        pygame.draw.rect(self.next_sprite, (90, 0, 0), (0, self.next_sprite.get_height(
        )-2, self.next_sprite.get_width(), 2))
        pygame.draw.rect(self.next_sprite, (255, 0, 0), (0, self.next_sprite.get_height(
        )-2, self.next_sprite.get_width()*(self.hp/100), 2))
