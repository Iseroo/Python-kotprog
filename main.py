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
        self.png = read_map_image("./map/level00.png")
    def run(self):

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.draw()
            self.update()
            
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
        
    def update(self):
        pygame.display.flip()
    
    def draw(self): 
        self.screen.fill((0, 0, 0))
        for x in range(300):
            for y in range(300):
                self.screen.set_at((x+100, y+100), self.png[x, y])
                
            
        
    
        
if __name__ == "__main__":
    
    game = Game()
    game.run()

    
    