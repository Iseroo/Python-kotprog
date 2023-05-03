import pygame
from cat_royale.classes.config import Config
from cat_royale.classes.event_stack import EventStack, Event, WindowStack


class Box:
    """

    Attributes:
        size (tuple): A tuple containing the width and height of the box.
        close_button (bool): Indicates if the box should have a close button. Default is True.
        close_callback (callable): The callback function to be executed when the box is closed.
        parent (Box): The parent class, if this box is a child. Default is None.
        Surface (pygame.Surface): The surface on which the box is drawn.
        position (tuple): The position of the box on the screen.
        opened (bool): Indicates if the box is currently open.
    """

    def __init__(self, size, close_button=True, close_callback=None, parent=None) -> None:
        """Initializes a new Box instance with the specified size and options."""
        self.size = size
        self._close_callback = None
        self.close_button = close_button
        self.close_callback = close_callback
        self.parent = parent
        self.Surface = pygame.Surface(size, pygame.SRCALPHA)
        self.Surface.fill((254, 211, 127))
        self.add_border()

        self.position = (0, 0)
        self._opened = False

        self.event_mouse_on = Event("Box_close_mouse_on", self.mouse_on_close)
        self.event_close = Event("close", self.close)

    @property
    def opened(self):
        return self._opened

    @opened.setter
    def opened(self, value):
        if value:
            self._opened = value
            if self.close_button:
                EventStack.push(self.event_mouse_on)
            EventStack.push(self.event_close)
            WindowStack.add_window(self)

            if self.parent:
                self.parent.opened = True
        else:
            self.close()

    def reset_surface(self):
        """Resets the surface of the box and fills it with its default color and border."""
        self.Surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.Surface.fill((254, 211, 127))
        self.add_border()

    @property
    def close_callback(self):
        """The callback function to be executed when the box is closed."""
        return self._close_callback

    @close_callback.setter
    def close_callback(self, value):
        """Sets the callback function to be executed when the box is closed."""
        self._close_callback = value

    def add_element(self, element, pos):
        """Adds a graphical element to the box at the specified position."""
        self.Surface.blit(element, pos)

    def reset_and_add(self, element, pos):
        """Resets the surface of the box and adds a graphical element at the specified position."""
        self.reset_surface()
        self.Surface.blit(element, pos)

    def add_border(self):
        """Adds a border to the box."""
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
        """Sets the close event callback function."""
        self.close_callback = event

    def close(self):
        """Closes the box and executes the close callback function if present."""
        self._opened = False
        if self._close_callback:
            self._close_callback()

        if self.parent:
            self.parent.opened = False
        EventStack.remove(self.event_mouse_on)
        EventStack.remove(self.event_close)
        WindowStack.remove_window(self)

    def mouse_on_close(self):
        """Handles mouse events when the mouse hovers over the close button."""
        mouse_pos = pygame.mouse.get_pos()
        if (mouse_pos[0] > self.position[0] + self.size[0]-20 and mouse_pos[0] < self.position[0] + self.size[0]
                and mouse_pos[1] > self.position[1] and mouse_pos[1] < self.position[1] + 20):
            Config.cursor_style = pygame.SYSTEM_CURSOR_HAND
            if pygame.mouse.get_pressed()[0]:

                self.close()

    def __call__(self, position=None):
        """Returns the surface of the box and updates its position if specified."""
        if self.close_button:
            if not EventStack.find_event(self.event_mouse_on):
                EventStack.push(self.event_mouse_on)
        if not EventStack.find_event(self.event_close):
            EventStack.push(self.event_close)

        if position:
            self.position = position

        return self.Surface
