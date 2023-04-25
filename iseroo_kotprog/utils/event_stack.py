from typing import List


class Event:
    def __init__(self, type: str, func: function) -> None:
        self.type = type
        self.func = func

    def __call__(self):
        self.func()


class EventStack:

    stack: List[Event] = []

    def push(event):

        EventStack.stack.append(event)

    def pop():

        return EventStack.stack.pop()

    def peek():

        return EventStack.stack[-1]

    def find(event_type):

        for event in EventStack.stack:

            if event.type == event_type:

                return event

        return None

    def find_and_call(event_type):

        event = EventStack.stack.rfind(lambda x: x['type'] == event_type)

        if event is not None:

            event()
