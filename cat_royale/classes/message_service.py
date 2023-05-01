

class MessageService:
    messages = []

    @staticmethod
    def add(message: dict) -> None:
        MessageService.messages.append(message)

    @staticmethod
    def get_messages():
        return MessageService.messages

    @staticmethod
    def next() -> dict:
        return MessageService.messages.pop(0) if len(MessageService.messages) > 0 else None
