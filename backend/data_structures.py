from __future__ import annotations

from typing import Generic, Iterator, List, TypeVar


T = TypeVar("T")


class Stack(Generic[T]):
    """Implementación de pila (LIFO) usando listas de Python."""

    def __init__(self) -> None:
        self._items: List[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("No se puede hacer pop en una pila vacía")
        return self._items.pop()

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("No se puede hacer peek en una pila vacía")
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def to_list(self) -> List[T]:
        return self._items.copy()


class Queue(Generic[T]):
    """Implementación de cola (FIFO) usando listas de Python."""

    def __init__(self) -> None:
        self._items: List[T] = []

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T:
        if self.is_empty():
            raise IndexError("No se puede hacer dequeue en una cola vacía")
        return self._items.pop(0)

    def front(self) -> T:
        if self.is_empty():
            raise IndexError("No se puede ver el frente de una cola vacía")
        return self._items[0]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    def to_list(self) -> List[T]:
        return self._items.copy()

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)
