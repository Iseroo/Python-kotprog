

import pygame


def get_item_sprite_image(sprite_sheet: pygame.Surface, row_index: int, count: int, sprite_size=32, spacing: int = 0):

    sprites = [pygame.Surface(
        (sprite_size, sprite_size), pygame.SRCALPHA) for x in range(count)]

    for i in range(count):

        sprites[i].blit(sprite_sheet, (0, 0), (i * (sprite_size + spacing), row_index * (sprite_size + spacing),
                                               sprite_size, sprite_size))

    return sprites


def scale_sprites(sprites: list, scale: float):
    return [pygame.transform.scale(x, (x.get_width() * scale, x.get_height() * scale)) for x in sprites]


def scale_image(image: pygame.Surface, scale: float):
    return pygame.transform.scale(image, (image.get_width() * scale, image.get_height() * scale))
