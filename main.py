import pygame
from pygame.locals import *
import sys
from utils.game_map import Block, GameMap
from utils.map_reader import *
from utils.message_service import *
from utils.item import *
from utils.config import Config
import webcolors
from utils.character import Character

pygame.init()


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))

        self.clock = pygame.time.Clock()
        self.running = True
        self.img_size, self.png = read_map_image(
            "./assets/images/map/level00.png")
        self.camera = pygame.Surface(
            (self.img_size[0]*40, self.img_size[1]*40))
        self.make_map()
        self.camera_pos = (0, 0)
        self.camera_speed = 5
        self.update_camera()
        self.character = Character()

    def run(self):

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.move_camera()
            self.move_character()
            self.screen.blit(self.camera, self.camera_pos)
            pygame.display.set_caption("FPS: " + str(self.clock.get_fps()))

            self.draw()
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
                if event.key == K_e:
                    pass
        self.message_service_subscribe()

    def update(self):
        pygame.display.flip()

    def draw(self):
        self.character.draw(self.screen)

    def message_service_subscribe(self):
        message = MessageService.next()
        if message:  # TODO: do something
            print(message)

    def make_map(self):
        self.game_map = GameMap()
        sprite_sheet = pygame.image.load(
            "./assets/images/items.png").convert_alpha()

        for x in range(0, self.img_size[0]):
            for y in range(0, self.img_size[1]):
                mapcolor = MAPCOLOR(
                    webcolors.rgb_to_hex(self.png[x, y]).upper())
                block = Block((x*Block.size, y*Block.size),
                              mapcolor)
                self.game_map.add_block(
                    block)

                if mapcolor != MAPCOLOR.GRASS and mapcolor != MAPCOLOR.WATER:
                    block.add_item(Item(get_item_sprite_image(
                        sprite_sheet, ITEM[mapcolor.name].value)))

    def move_camera(self):
        keys = pygame.key.get_pressed()

        if keys[K_LEFT]:
            self.camera_pos = (
                self.camera_pos[0] + self.camera_speed, self.camera_pos[1])
        if keys[K_RIGHT]:
            self.camera_pos = (
                self.camera_pos[0] - self.camera_speed, self.camera_pos[1])
        if keys[K_UP]:
            self.camera_pos = (
                self.camera_pos[0], self.camera_pos[1] + self.camera_speed)
        if keys[K_DOWN]:
            self.camera_pos = (
                self.camera_pos[0], self.camera_pos[1] - self.camera_speed)
        if self.camera_pos[0] > 0:
            self.camera_pos = (0, self.camera_pos[1])

        if self.camera_pos[1] > 0:
            self.camera_pos = (self.camera_pos[0], 0)

        if self.camera_pos[0] < -self.camera.get_width() + self.screen.get_width():
            self.camera_pos = (-self.camera.get_width() +
                               self.screen.get_width(), self.camera_pos[1])

        if self.camera_pos[1] < -self.camera.get_height() + self.screen.get_height():
            self.camera_pos = (
                self.camera_pos[0], -self.camera.get_height() + self.screen.get_height())

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
        self.game_map.draw(self.camera)


if __name__ == "__main__":
    Config.load("./config/config.json")
    game = Game()
    game.run()
