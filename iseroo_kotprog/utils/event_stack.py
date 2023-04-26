from typing import List


class Event:
    def __init__(self, type: str, func, *args) -> None:
        self.type = type
        self.func = func
        self.args = args

    def __call__(self):
        self.func(*self.args)

    def __str__(self) -> str:
        return self.type + " " + str(self.func)


class EventStack:

    stack: List[Event] = []

    def push(event):

        EventStack.stack.append(event)

    def pop():

        return EventStack.stack.pop()

    def remove(event):
        # print(event, event in EventStack.stack)
        try:
            EventStack.stack.remove(event)
        except:
            pass

    def peek():

        return EventStack.stack[-1]

    def find(event_type):

        for event in EventStack.stack:

            if event.type == event_type:

                return event

        return None

    def find_and_call(event_type):

        event = next(
            (x for x in EventStack.stack[::-1] if x.type == event_type), None)

        if event is not None:

            event()

    def iterate():

        for event in EventStack.stack:

            event()

    def call_last():

        EventStack.stack[-1]()

    def call_and_pop(event_type):
        event = next(
            (x for x in EventStack.stack[::-1] if x.type == event_type), None)

        if event is not None:

            event()
            EventStack.remove(event)


class WindowStack:

    stack = []

    def add_window(window):
        WindowStack.stack.append(window)

    def remove_window(window):
        WindowStack.stack.remove(window)
