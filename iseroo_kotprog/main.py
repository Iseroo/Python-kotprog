import random
from typing import Sequence
import pygame
from pygame.locals import *
import sys
from utils.functions import scale_image
from utils.game_map import Block, GameMap
from utils.health_bars import HealthBar
from utils.inventory import InventoryHUD, Inventory, CraftingHUD
from utils.map_reader import *
from utils.message_service import *
from utils.item import *
from utils.config import Config
import webcolors
from utils.character import Character, Enemy
from utils.text_display import PlayerInfoText, TextDisplay
from utils.box import Box
from utils.event_stack import *

pygame.init()


class Game:

    def __init__(self):
        self.screen = pygame.display.set_mode(
            (Config.data["screen_size"]["width"], Config.data["screen_size"]["height"]))
        Config.screen = self.screen
        self.loading_text = TextDisplay(
            "Loading...", 30, (255, 255, 255))
        self.loadingScreen = pygame.image.load(Config.images["loading_screen"])
        self.screen.blit(self.loadingScreen, (self.screen.get_width()//2 -
                                              self.loadingScreen.get_width()//2, self.screen.get_height()//2 - self.loadingScreen.get_height()//2))
        self.screen.blit(self.loading_text.Surface, (self.screen.get_width()//2 - self.loading_text.Surface.get_width() //
                         2, self.screen.get_height()//2 - self.loading_text.Surface.get_height()//2 - 200))
        pygame.display.flip()
        EventStack.push(Event("close", self.close))

        self.clock = pygame.time.Clock()
        self.running = True
        self.craftHud_toggle = False

        self.img_size, self.png = read_map_image(
            Config.images["level00"])

        self.screen_layer = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))

        self.map_layer = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))
        Config.map_layer = self.map_layer
        self.camera = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))
        self.make_map()
        self.camera_pos = (0, 0)
        self.camera_speed = 5
        self.update_camera()

        self.items = {}
        self.load_items()

        self.character = Character()
        Config.all_characters.append(self.character)

        self.enemies = [Enemy() for _ in range(10)]
        Config.all_characters.extend(self.enemies)
        for x in self.enemies:
            x.position = self.game_map.get_block_by_indexes(
                (random.randint(0, 99), random.randint(0, 99))).coords
        # self.enemies[0].position = self.game_map.get_block_by_indexes(
        #     (10, 10)).coords

        self.health_bar = HealthBar(
            (self.screen.get_width() // 2, self.screen.get_height()-80))

        self.player_info_text_display = PlayerInfoText(
            (self.character.get_position()[0], self.character.get_position()[1]-20))

        self.onblock = None

        self.game_over = False
        self.game_over_text = TextDisplay("Game Over", 24, (255, 0, 0))
        self.game_over_dialog = Box(
            (self.screen.get_width(), self.screen.get_height()), close_callback=self.close)
        self.game_over_dialog.add_element(self.game_over_text.Surface, (self.game_over_dialog.Surface.get_width(
        )//2-self.game_over_text.Surface.get_width()//2, self.game_over_dialog.Surface.get_height()//2-self.game_over_text.Surface.get_height()//2))

        self.minimap_img = pygame.image.load(Config.images["level00"])
        self.minimap = Box(
            (200, 200), close_button=False)

        self.minimap.position = (self.screen.get_width()-200,
                                 self.screen.get_height()-200)
        self.minimap.opened = True

    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def run(self):

        while self.running:

            Config.cursor_style = None
            self.clock.tick(60)
            self.move_camera()
            self.move_character()
            pygame.display.set_caption("FPS: " + str(self.clock.get_fps()))
            self.draw()

            self.handle_events()
            # print(self.game_map.get_block_by_coords(
            # pygame.mouse.get_pos()).indexes)
            self.enemy_ai_updates()
            if Config.cursor_style:
                pygame.mouse.set_cursor(Config.cursor_style)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.update()

    def handle_events(self):

        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    EventStack.call_and_pop("close")

                if event.key == K_q:
                    dropped_item = self.character.inventory.remove_item_from_slot(
                        self.character.inventory_hud.selected_slot)
                    self.character.inventory_hud.update_slots()
                    if self.character.onblock and dropped_item:

                        self.character.onblock.add_item(dropped_item)
                        self.character.onblock.draw(self.map_layer)
                if event.key == K_f:
                    self.character.pickup(self.map_layer)

                if event.key == K_c:
                    self.character.use_slot()

                if event.key == K_m:
                    self.minimap.opened = not self.minimap.opened

                if event.key == K_e:
                    self.character.crafting_hud.toggle()
                    # self.toggle_craft_hud()
                if event.key == K_h:
                    [print(x.type) for x in EventStack.stack]
                if event.key == K_SPACE:
                    self.character.do_attack = True
                    self.character.use_weapon_to_attack()
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.character.inventory_hud.select_slot(
                        self.character.inventory_hud.selected_slot + 1)
                elif event.y < 0:
                    self.character.inventory_hud.select_slot(
                        self.character.inventory_hud.selected_slot - 1)

        EventStack.find_and_call("Box_close_mouse_on")
        self.message_service_subscribe()

    def minimap_player(self):
        if self.character.onblock:

            self.character.onblock.indexes
            # draw rect on minimap_img
            copy = self.minimap_img.copy()
            pygame.draw.rect(copy, (0, 0, 255),
                             (*self.character.onblock.indexes, 2, 2))
            for enemy in self.enemies:
                if enemy.onblock and enemy.hp > 0:
                    pygame.draw.rect(copy, (0, 255, 255),
                                     (*enemy.onblock.indexes, 2, 2))
            copy = scale_image(copy, 1.5)

            self.minimap.Surface.blit(copy, (25, 25))

    def enemy_ai_updates(self):
        # for enemy in self.enemies:
        #     enemy.auto_move_to_pos(self.character.position)

        for enemy in self.enemies:
            enemy.ai(self.map_layer)

    def update(self):
        self.character.set_onblock(self.onblock_for_character(self.character))
        # self.enemy.set_onblock(self.onblock_for_character(self.enemy))
        for enemy in self.enemies:
            enemy.set_onblock(self.onblock_for_character(enemy))

        self.player_info_text_display.set_coords(
            (self.character.get_position()[0], self.character.get_position()[1]-20))

        self.health_bar.update(*self.character.get_health())

        if self.character.get_health()[0] <= 0:
            self.game_over = True
            self.character.position = (
                self.screen.get_width()//2-self.character.next_sprite.get_width()//2, self.screen.get_height()//2-100)

        pygame.display.flip()

    def onblock_for_character(self, character):
        return self.game_map.on_block_check(character.get_position(), self.map_layer, camera_pos=self.camera_pos)

    def draw(self):
        if self.game_over:
            self.screen.blit(self.game_over_dialog.Surface, (0, 0))
            self.character.draw(self.screen)
            return
        self.screen.fill(MAPCOLOR.GRASS.rgb(MAPCOLOR.GRASS.value))
        self.screen_layer.blit(self.map_layer, (0, 0))
        self.character.draw(self.screen_layer)
        # self.enemy.draw(self.screen_layer)
        for enemy in self.enemies:
            # print(self.screen_layer)
            enemy.draw(self.screen_layer)
        self.player_info_text_display.draw(self.screen_layer)
        self.screen.blit(self.screen_layer, self.camera_pos)

        self.character.inventory_hud.draw(self.screen)

        self.health_bar.draw(self.screen)
        if self.minimap.opened:
            self.minimap_player()
        for dialog in WindowStack.stack:
            if dialog.opened:
                self.screen.blit(dialog.Surface, dialog.position)

        if self.character.crafting_hud.box.opened:

            self.screen.blit(self.character.crafting_hud.Surface(),
                             self.character.crafting_hud.Surface.position)

        # if self.random_box_visible:
        #     self.screen.blit(self.random_box(), self.random_box.position)

        # [self.screen.blit(box(), (0, 0)) for box in self.boxes]

    def message_service_subscribe(self):
        message = MessageService.next()
        if message:  # TODO: do something
            color = (249, 113, 50) if message["severity"] == "warning" else (
                255, 0, 0) if message["severity"] == "error" else (255, 255, 255)
            text = TextDisplay(
                message["text"], 12, color)
            try:

                duration = message["duration"]
            except:
                duration = 100
            self.player_info_text_display.add(
                text, duration)

    def make_map(self):
        self.game_map = GameMap()
        Config.game_map = self.game_map
        sprite_sheet = pygame.image.load(
            Config.images["items"]).convert_alpha()

        for x in range(0, self.img_size[0]):
            for y in range(0, self.img_size[1]):
                mapcolor = MAPCOLOR(
                    webcolors.rgb_to_hex(self.png[x, y]).upper())
                block = Block((x*Block.size, y*Block.size),
                              mapcolor)
                self.game_map.add_block(
                    block)

                if mapcolor != MAPCOLOR.GRASS:
                    if mapcolor == MAPCOLOR.CARROT:
                        block.add_item(Food(get_map_sprite_image(
                            sprite_sheet, ITEM[mapcolor.name].value), mapcolor.name, Config.data["items_stack_size"][mapcolor.name], Config.data["food_health_bonus"]["CARROT"][0], Config.data["food_health_bonus"]["CARROT"][1]))

                    elif mapcolor == MAPCOLOR.BERRY:
                        block_type = random.choice(
                            [ITEM["APPLE"], ITEM["BERRY"], ITEM["MUSHROOM"], ITEM["BERRY"]])
                        block.add_item(Food(get_map_sprite_image(
                            sprite_sheet, block_type.value), mapcolor.name, Config.data["items_stack_size"][mapcolor.name], Config.data["food_health_bonus"][block_type.name][0], Config.data["food_health_bonus"][block_type.name][1]))
                    else:
                        block.add_item(Material(get_map_sprite_image(
                            sprite_sheet, ITEM[mapcolor.name].value), mapcolor.name, Config.data["items_stack_size"][mapcolor.name]))

    def move_camera(self, keys=None, speed=1):
        keys = pygame.key.get_pressed() if keys == None else keys

        if keys[K_LEFT]:
            self.camera_pos = (
                self.camera_pos[0] + (self.camera_speed + (1 * speed)), self.camera_pos[1])
            self.check_camera_pos()
        if keys[K_RIGHT]:
            self.camera_pos = (
                self.camera_pos[0] - (self.camera_speed + (1 * speed)), self.camera_pos[1])
            self.check_camera_pos()
        if keys[K_UP]:
            self.camera_pos = (
                self.camera_pos[0], self.camera_pos[1] + (self.camera_speed + (1 * speed)))
            self.check_camera_pos()
        if keys[K_DOWN]:
            self.camera_pos = (
                self.camera_pos[0], self.camera_pos[1] - (self.camera_speed + (1 * speed)))
            self.check_camera_pos()

    def check_camera_pos(self):

        if self.camera_pos[0] > 0 + Config.data["camera_offset"]["x"]:
            self.camera_pos = (
                0 + Config.data["camera_offset"]["x"], self.camera_pos[1])
        if self.camera_pos[0] < -self.camera.get_width() + Config.data["screen_size"]["width"] - Config.data["camera_offset"]["x"]:
            self.camera_pos = (-self.camera.get_width() +
                               Config.data["screen_size"]["width"] - Config.data["camera_offset"]["x"], self.camera_pos[1])
        if self.camera_pos[1] > 0 + Config.data["camera_offset"]["y"]:
            self.camera_pos = (
                self.camera_pos[0], 0 + Config.data["camera_offset"]["y"])
        if self.camera_pos[1] < -self.camera.get_height() + Config.data["screen_size"]["height"] - Config.data["camera_offset"]["y"]:
            self.camera_pos = (self.camera_pos[0], -self.camera.get_height() +
                               Config.data["screen_size"]["height"] - Config.data["camera_offset"]["y"])

    def move_character(self):  # move with wasd

        keys = pygame.key.get_pressed()

        if keys[K_a]:
            self.character.move("left")
        if keys[K_d]:
            self.character.move("right")
        if keys[K_w]:
            self.character.move("up")
        if keys[K_s]:
            self.character.move("down")

        keys = {K_LEFT: False, K_RIGHT: False, K_UP: False, K_DOWN: False}

        character_pos = (
            self.character.position[0] + self.camera_pos[0] + Config.data["camera_offset"]["x"], self.character.position[1] + self.camera_pos[1] + Config.data["camera_offset"]["y"])

        if character_pos[0] < 0 + Config.data["camera_offset"]["x"]:

            keys[K_LEFT] = True
        if character_pos[0] > Config.data["screen_size"]["width"] - Config.data["camera_offset"]["x"]:

            keys[K_RIGHT] = True
        if character_pos[1] < 0 + Config.data["camera_offset"]["y"]:

            keys[K_UP] = True
        if character_pos[1] > Config.data["screen_size"]["height"] - Config.data["camera_offset"]["y"]:

            keys[K_DOWN] = True
        self.move_camera(keys, speed=100)

    def update_camera(self):
        self.game_map.draw(self.map_layer)

    def load_items(self):
        sprite_sheet = pygame.image.load(
            Config.images["items"]).convert_alpha()
        for item in ITEM:
            self.items[item.name] = get_map_sprite_image(
                sprite_sheet, ITEM[item.name].value)


if __name__ == "__main__":
    Config.load("./config/config.json")
    Config.load_image_locations("./assets/image_locations.json")
    Config.cursor_style

    game = Game()

    game.run()
