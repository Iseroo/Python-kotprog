

import pygame


class TextDisplay:
    def __init__(self, text, font_size, color, outline_color=(0, 0, 0)) -> None:
        self.text = text
        self.font_size = font_size
        self.color = color
        self.outline_color = outline_color

        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        self.text_surface = self.font.render(
            self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect()

        self.outline_surface = self.font.render(
            self.text, True, self.outline_color)

    def draw(self):
        surface = pygame.Surface(
            (self.text_rect.width+1, self.text_rect.height+1), pygame.SRCALPHA)
        surface.blit(self.outline_surface, (1, 1))
        surface.blit(self.text_surface, (0, 0))
        return surface


class PlayerInfoText:
    def __init__(self, coords) -> None:
        # {"text":TextDisplay, "duration":int, "coords": tuple}
        self.stack = []
        self.default_coords = coords

    def add(self, text: TextDisplay, duration: int):
        self.stack.append(
            {"text": text, "duration": duration})

    def draw(self, screen: pygame.Surface):
        for text in self.stack:
            screen.blit(text["text"].draw(), self.default_coords)
            text["duration"] -= 1
            self.default_coords = (
                self.default_coords[0], self.default_coords[1] - 20)
            if text["duration"] <= 0:
                self.stack.remove(text)
                self.default_coords = (
                    self.default_coords[0], self.default_coords[1] + 20)

    def set_coords(self, coords: tuple):
        self.default_coords = coords
