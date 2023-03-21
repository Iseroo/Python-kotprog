import pygame
from pygame.locals import *
import sys
from utils.map_reader import *


pygame.init()   


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.running = True
        
    def run(self):

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
            
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
        
    def update(self):
        pass
    
    def draw(self): 
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        
if __name__ == "__main__":
    png = read_map_image("./map/level00.png")
    for x in range(100):
        for y in range(100):
            print(png[x, y])

    
    