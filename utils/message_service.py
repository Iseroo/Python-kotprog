from typing import MutableSequence, TypedDict


class Message(TypedDict):
    """Message interface

    {'text': str, 'severity': str} -> Message

    Members: 
        text (str): message text\n
        severity ("info" or "warning" or "error"): message severity
    """

    text: str
    severity: str
    duration: int


class MessageService:
    messages: MutableSequence[Message] = []

    @staticmethod
    def add(message: Message) -> None:
        MessageService.messages.append(message)

    @staticmethod
    def get_messages() -> MutableSequence[Message]:
        return MessageService.messages

    @staticmethod
    def clear_messages() -> None:
        messages = []

    @staticmethod
    def next() -> Message:
        return MessageService.messages.pop(0) if len(MessageService.messages) > 0 else None
