from enum import Enum
 
class ITEM(Enum):
    ITEM1 = 1
    ITEM2 = 2
    ITEM3 = 3

class Item:
    def __init__(self, stack_size: int, item_type: ITEM) -> None:
        self.count = 0
        self.max = stack_size
        
    def pickup(self) -> None:
        if self.count < self.max:
            self.count += 1
        else:
            raise Exception("Item stack is full")
    
