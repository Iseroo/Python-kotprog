import random
import pygame
from pygame.locals import *
import sys
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

        self.clock = pygame.time.Clock()
        self.running = True
        self.craftHud_toggle = False

        self.img_size, self.png = read_map_image(
            Config.images["level00"])

        self.screen_layer = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))

        self.map_layer = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))
        self.camera = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))
        self.make_map()
        self.camera_pos = (0, 0)
        self.camera_speed = 5
        self.update_camera()

        self.items = {}
        self.load_items()

        self.character = Character()
        self.character.add_event_to_craft_hud(
            self.toggle_craft_hud)

        self.enemies = [Enemy() for _ in range(0)]
        for x in self.enemies:
            x.position = self.game_map.get_block_by_indexes(
                (random.randint(5, 30), random.randint(5, 30))).coords
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

        self.random_box_is_visible = True
        self.random_box = Box(
            (200, 200), close_callback=self.random_box_visible)
        self.random_box.position = (self.screen.get_width()//2-100,
                                    self.screen.get_height()//2-100)
        self.random_box.opened = True

    def random_box_visible(self):
        self.random_box_is_visible = False

    def close(self):
        self.running = False
        pygame.quit()
        sys.exit()

    def run(self):

        while self.running:
            EventStack.stack = [Event("close", self.close)]

            if self.random_box_is_visible:
                EventStack.stack.append(Event(
                    "Box_close_mouse_on", self.random_box, self.random_box.position))
                EventStack.stack.append(Event(
                    "close", self.random_box_visible))
            WindowStack.stack = []
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

                if event.key == K_SPACE:
                    MessageService.add(
                        {"text": "Inventory is full", "severity": "warning"})
                    MessageService.add(
                        {"text": "Inventory is full", "severity": "error"})
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

                if event.key == K_e:
                    self.toggle_craft_hud()

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.character.inventory_hud.select_slot(
                        self.character.inventory_hud.selected_slot + 1)
                elif event.y < 0:
                    self.character.inventory_hud.select_slot(
                        self.character.inventory_hud.selected_slot - 1)
        EventStack.find_and_call("Box_close_mouse_on")
        self.message_service_subscribe()

    def enemy_ai_updates(self):
        for enemy in self.enemies:
            enemy.auto_move_to_pos(self.character.position)

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
        return self.game_map.on_block_check(character.get_position(), self.map_layer)

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

        WindowStack.add_window(self.character.crafting_hud.box)
        WindowStack.add_window(self.random_box)

        for dialog in WindowStack.stack:
            if dialog.opened:
                self.screen.blit(dialog.Surface, dialog.position)

        self.character.crafting_hud.box.opened = self.craftHud_toggle
        if self.craftHud_toggle:

            self.character.crafting_hud.draw(self.screen)

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

                if mapcolor != MAPCOLOR.GRASS and mapcolor != MAPCOLOR.WATER:
                    if mapcolor == MAPCOLOR.BERRY:
                        block.add_item(Food(get_map_sprite_image(
                            sprite_sheet, ITEM[mapcolor.name].value), mapcolor.name, Config.data["items_stack_size"][mapcolor.name], Config.data["food_health_bonus"]["BERRY"][0], Config.data["food_health_bonus"]["BERRY"][1]))
                    else:
                        block.add_item(Item(get_map_sprite_image(
                            sprite_sheet, ITEM[mapcolor.name].value), mapcolor.name, Config.data["items_stack_size"][mapcolor.name]))

    def move_camera(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT]:
            self.camera_pos = (
                self.camera_pos[0] + self.camera_speed, self.camera_pos[1])
            self.check_camera_pos()
        if keys[K_RIGHT]:
            self.camera_pos = (
                self.camera_pos[0] - self.camera_speed, self.camera_pos[1])
            self.check_camera_pos()
        if keys[K_UP]:
            self.camera_pos = (
                self.camera_pos[0], self.camera_pos[1] + self.camera_speed)
            self.check_camera_pos()
        if keys[K_DOWN]:
            self.camera_pos = (
                self.camera_pos[0], self.camera_pos[1] - self.camera_speed)
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

    def update_camera(self):
        self.game_map.draw(self.map_layer)

    def load_items(self):
        sprite_sheet = pygame.image.load(
            Config.images["items"]).convert_alpha()
        for item in ITEM:
            self.items[item.name] = get_map_sprite_image(
                sprite_sheet, ITEM[item.name].value)

    def toggle_craft_hud(self):
        self.craftHud_toggle = not self.craftHud_toggle


if __name__ == "__main__":
    Config.load("./config/config.json")
    Config.load_image_locations("./assets/image_locations.json")
    Config.cursor_style

    game = Game()

    game.run()
