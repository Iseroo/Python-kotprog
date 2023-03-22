from typing import MutableSequence

class MessageService:
    def __init__(self) -> None:
        self.messages: MutableSequence[str] = []
        
    def add_message(self, message: str) -> None:
        self.messages.append(message)
        
    def get_messages(self) -> MutableSequence[str]:
        return self.messages
    
    def clear_messages(self) -> None:
        self.messages = []
        
    def get_next_message(self) -> str:
        return self.messages.pop(0)
        