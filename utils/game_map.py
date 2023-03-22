from item import Item
from typing import *


class Block:
    def __init__(self) -> None:
        self.items: MutableSequence[Item] = []


class GameMap:
    def __init__(self) -> None:
        self.blocks: MutableSequence[Block] = []
        