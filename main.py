import random
import pygame
from pygame.locals import *
import sys
from utils.game_map import Block, GameMap
from utils.health_bars import HealthBar
from utils.inventory import InventoryHUD, Inventory
from utils.map_reader import *
from utils.message_service import *
from utils.item import *
from utils.config import Config
import webcolors
from utils.character import Character
from utils.text_display import PlayerInfoText, TextDisplay

pygame.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (Config.data["screen_size"]["width"], Config.data["screen_size"]["height"]))

        self.clock = pygame.time.Clock()
        self.running = True
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

        self.health_bar = HealthBar(
            (self.screen.get_width() // 2, self.screen.get_height()-80))

        self.player_info_text_display = PlayerInfoText(
            (self.character.get_position()[0], self.character.get_position()[1]-20))

        self.inventory = Inventory()

        self.inventory.add_item_to_stack(
            Item(self.items['CARROT'], 'CARROT', 1))

        self.inventory_hud = InventoryHUD(self.inventory)
        self.inventory_hud.update_slots()

        self.onblock = None

    def run(self):

        while self.running:
            self.clock.tick(60)
            self.move_camera()
            self.move_character()
            pygame.display.set_caption("FPS: " + str(self.clock.get_fps()))
            self.draw()
            self.handle_events()
            self.update()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                if event.key == K_SPACE:
                    MessageService.add(
                        {"text": "Inventory is full", "severity": "warning"})
                    MessageService.add(
                        {"text": "Inventory is full", "severity": "error"})
                if event.key == K_q:
                    dropped_item = self.inventory.remove_item_from_slot(
                        self.inventory_hud.selected_slot)
                    self.inventory_hud.update_slots()
                    if self.onblock and dropped_item:

                        self.onblock.add_item(dropped_item)
                        self.onblock.draw(self.map_layer)
                if event.key == K_f:
                    if self.onblock:
                        picked_up = self.onblock.remove_item_from_top()
                        if picked_up:
                            self.inventory.add_item_to_stack(picked_up)
                            self.inventory_hud.update_slots()
                            self.onblock.draw(self.map_layer)

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.inventory_hud.select_slot(
                        self.inventory_hud.selected_slot + 1)
                elif event.y < 0:
                    self.inventory_hud.select_slot(
                        self.inventory_hud.selected_slot - 1)

        self.message_service_subscribe()

    def update(self):
        self.onblock = self.game_map.on_block_check(
            self.character.get_position(), self.map_layer)
        self.player_info_text_display.set_coords(
            (self.character.get_position()[0], self.character.get_position()[1]-20))

        self.health_bar.update(*self.character.get_health())
        pygame.display.flip()

    def draw(self):
        self.screen.fill(MAPCOLOR.GRASS.rgb(MAPCOLOR.GRASS.value))
        self.screen_layer.blit(self.map_layer, (0, 0))
        self.character.draw(self.screen_layer)
        self.player_info_text_display.draw(self.screen_layer)
        self.screen.blit(self.screen_layer, self.camera_pos)

        self.inventory_hud.draw(self.screen)
        self.health_bar.draw(self.screen)

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


if __name__ == "__main__":
    Config.load("./config/config.json")
    Config.load_image_locations("./assets/image_locations.json")
    game = Game()
    game.run()
