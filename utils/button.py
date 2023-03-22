from typing import Callable


class Button:
    def __init__(self, text, func: Callable, position: tuple) -> None:
        self.text = text
        self.func = func
        self.position = position

    def draw(self):
        pass

    def run_function(self, *args):
        self.func(*args)

    def clicked(self, mouse_postion: tuple):
        if mouse_postion[0] > self.position[0] and mouse_postion[0] < self.position[0] + self.width:
            if mouse_postion[1] > self.position[1] and mouse_postion[1] < self.position[1] + self.height:
                return True
        return False
