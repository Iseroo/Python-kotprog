
from ordered_set import OrderedSet


class Event:
    def __init__(self, event_type: str, func, *args) -> None:
        self.type = event_type
        self.func = func
        self.args = args

    def __call__(self):
        self.func(*self.args)

    def __str__(self) -> str:
        return self.type + " " + str(self.func)


class EventStack:

    stack = OrderedSet()

    @staticmethod
    def push(event):

        EventStack.stack.add(event)

    @staticmethod
    def pop(index=-1):

        return EventStack.stack.pop(index)

    @staticmethod
    def remove(event):
        try:
            EventStack.stack.discard(event)
        except KeyError:
            print("Not in")

    @staticmethod
    def peek(index=-1):

        return EventStack.stack[index]

    @staticmethod
    def find(event_type):

        for event in EventStack.stack:

            if event.type == event_type:

                return event

        return None

    @staticmethod
    def find_event(event):

        for e in EventStack.stack:

            if e == event:

                return e

        return None

    @staticmethod
    def find_and_call(event_type):

        event = next(
            (x for x in EventStack.stack[::-1] if x.type == event_type), None)

        if event is not None:

            event()

    @staticmethod
    def iterate():

        for event in EventStack.stack:

            event()

    @staticmethod
    def call_last():

        event = EventStack.stack[-1]
        event()

    @staticmethod
    def call_and_pop(event_type):
        event = next(
            (x for x in EventStack.stack[::-1] if x.type == event_type), None)

        if event is not None:

            EventStack.remove(event)
            event()


class WindowStack:

    stack = []

    @staticmethod
    def add_window(window):
        WindowStack.stack.append(window)

    @staticmethod
    def remove_window(window):
        WindowStack.stack.remove(window)
