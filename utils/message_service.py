from typing import MutableSequence

class MessageService:
    messages: MutableSequence[str] = []
    
    @staticmethod    
    def add(message: str) -> None:
        MessageService.messages.append(message)
       
    @staticmethod
    def get_messages() -> MutableSequence[str]:
        return MessageService.messages
    
    @staticmethod
    def clear_messages() -> None:
        messages = []
        
    @staticmethod
    def next() -> str:
        
        return MessageService.messages.pop(0) if len(MessageService.messages) > 0 else None
        