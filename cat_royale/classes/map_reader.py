
from PIL import Image
import pygame


def read_map_image(map_image):

    map_image = Image.open(map_image)
    map_image = map_image.convert('RGB')
    res = map_image.load()
    return (map_image.size, res)


def get_map_sprite_image(sprite_sheet: pygame.Surface, index: tuple, sprite_size=32):

    sprite = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
    sprite.blit(sprite_sheet, (0, 0),
                (index[1] * sprite_size, index[0] * sprite_size, sprite_size, sprite_size))

    return sprite
