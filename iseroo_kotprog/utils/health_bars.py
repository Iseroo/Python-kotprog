import pygame


class HealthBar:
    def __init__(self, position, hp=100, hunger=100) -> None:
        self._hp = hp
        self._hunger = hunger
        self.position = position
        self.bar_widht = 170  # px
        self.bar_height = 5  # px
        self.bar_gap = 30  # px

        self.hp_surface = pygame.Surface((self.bar_widht, self.bar_height))
        self.hunger_surface = pygame.Surface((self.bar_widht, self.bar_height))
        self.make_bar_surfaces()

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, hp):
        if hp >= 0 or hp <= 100:
            self._hp = hp
            self.make_bar_surfaces()

    @property
    def hunger(self):
        return self._hunger

    @hunger.setter
    def hunger(self, hunger):
        if hunger >= 0 or hunger <= 100:
            self._hunger = hunger
            self.make_bar_surfaces()

    def update(self, hp, hunger):
        self.hp = hp
        self.hunger = hunger

    def make_bar_surfaces(self):
        # make hp surface with the right color, and a lighter one for the background
        # and make hunger surface with the right color, and a lighter one for the background

        self.hp_surface.fill((100, 0, 0))
        hp_rect = pygame.Rect(
            (0, 0), (self.bar_widht * self.hp / 100, self.bar_height))
        pygame.draw.rect(self.hp_surface, (255, 0, 0), hp_rect)

        self.hunger_surface.fill((0, 0, 100))
        hunger_rect = pygame.Rect(
            (0, 0), (self.bar_widht * self.hunger / 100, self.bar_height))

        pygame.draw.rect(self.hunger_surface, (0, 0, 255), hunger_rect)

    def draw(self, screen):
        position = (
            self.position[0] - ((self.bar_widht * 2 + self.bar_gap)//2), self.position[1])
        screen.blit(self.hp_surface, position)
        screen.blit(self.hunger_surface,
                    (position[0] + self.hp_surface.get_width() + self.bar_gap, position[1]))
