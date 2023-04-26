
import pygame
from utils.config import Config
from utils.event_stack import *


class Box:
    def __init__(self, size, close_button=True, close_callback=None) -> None:
        self.size = size
        self.Surface = pygame.Surface(size, pygame.SRCALPHA)
        self.Surface.fill((254, 211, 127))
        self._close_callback = None
        self.close_callback = close_callback
        self.position = (0, 0)
        self.close_button = close_button
        self.add_border()
        self.opened = False

    @property
    def close_callback(self):
        return self._close_callback

    @close_callback.setter
    def close_callback(self, value):
        self._close_callback = value

        self.event_mouse_on = Event("Box_close_mouse_on", self.mouse_on_close)
        EventStack.push(self.event_mouse_on)

        self.event_close = Event("close", self.close)
        EventStack.push(self.event_close)

    def add_element(self, element, pos):
        self.Surface.blit(element, pos)

    def add_border(self):
        # draw border left, right, bottom is 2px wide and rgb(51,32,24), top is 2px wide and rbg(76,48,36). innerborder 4px wide, and rbg(153,69,63)
        pygame.draw.rect(self.Surface, (51, 32, 24),
                         (0, 0, self.size[0], self.size[1]), 2, 2, 2, 2)
        pygame.draw.rect(self.Surface, (76, 48, 36),
                         (0, 0, self.size[0], 2))

        pygame.draw.rect(self.Surface, (153, 69, 63),
                         (2, 2, self.size[0]-4, self.size[1]-4), 4, 4, 4, 4)

        pygame.draw.rect(self.Surface, (51, 32, 24),
                         (4, 4, self.size[0]-8, self.size[1]-8), 2, 2, 2, 2)

        if self.close_button:
            pygame.draw.rect(self.Surface, (254, 211, 127),
                             (self.size[0]-20, 0, 20, 20))
            pygame.draw.line(self.Surface, (0, 0, 0),
                             (self.size[0]-20, 0), (self.size[0], 20), 2)
            pygame.draw.line(self.Surface, (0, 0, 0),
                             (self.size[0], 0), (self.size[0]-20, 20), 2)

    def set_close_event(self, event):
        self.close_callback = event

    def close(self):
        self.opened = False
        if self.close_callback:
            # print("close")

            self.close_callback()
            EventStack.remove(self.event_mouse_on)
            EventStack.remove(self.event_close)

    def mouse_on_close(self):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > self.position[0] + self.size[0]-20 and mouse_pos[0] < self.position[0] + self.size[0] and mouse_pos[1] > self.position[1] and mouse_pos[1] < self.position[1] + 20:
            Config.cursor_style = pygame.SYSTEM_CURSOR_HAND
            if pygame.mouse.get_pressed()[0]:

                self.close()

    def __call__(self, position):
        self.event_mouse_on = Event("Box_close_mouse_on", self.mouse_on_close)
        EventStack.push(self.event_mouse_on)

        self.event_close = Event("close", self.close)
        EventStack.push(self.event_close)
        if not self.close_button:
            return
        self.position = position
        self.mouse_on_close()

        return self.Surface