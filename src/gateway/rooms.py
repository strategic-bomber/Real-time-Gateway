from asyncio import Queue, QueueFull

from .models import EventInput

EventQueue = Queue[EventInput]

class Room:
    def __init__(self) -> None:
        self._subscribers: set[EventQueue] = set()

    def subscribe(self, queue: EventQueue) -> None:
        self._subscribers.add(queue)

    def unsubscribe(self, queue: EventQueue) -> None:
        self._subscribers.discard(queue)

    def publish(self, event: EventInput) -> list[EventQueue]:
        full_queues: list[EventQueue] = []

        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except QueueFull:
                full_queues.append(queue)

        return full_queues
