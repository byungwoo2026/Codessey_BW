"""직접 구현한 이중 연결 리스트 모듈.

Mini Redis에서는 LRU를 추적해야 한다. 가장 최근에 사용한 key는
리스트 앞(head)에 두고, 가장 오래 사용하지 않은 key는 뒤(tail)에 둔다.
그러면 메모리가 부족할 때 tail만 제거하면 LRU key를 O(1)에 찾을 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Node:
    """이중 연결 리스트의 노드.

    prev는 이전 노드, next는 다음 노드를 가리킨다. 양쪽 방향으로
    연결되어 있으므로 중간 노드도 O(1)에 제거하거나 이동할 수 있다.
    """

    data: Any
    prev: Node | None = None
    next: Node | None = None


class DoublyLinkedList:
    """LRU(Least Recently Used) 순서를 O(1)로 관리하기 위한 이중 연결 리스트.

    head 쪽이 가장 최근 사용, tail 쪽이 가장 오래된 사용이다.
    SET/GET으로 key가 사용되면 move_to_front()로 head로 옮긴다.
    """

    def __init__(self) -> None:
        """빈 리스트를 만든다."""
        self.head: Node | None = None
        self.tail: Node | None = None
        self._size = 0

    def size(self) -> int:
        """현재 노드 개수를 반환한다."""
        return self._size

    def insert_front(self, data: Any) -> Node:
        """새 데이터를 head 앞에 넣고 생성된 노드를 반환한다.

        LRU 기준으로는 '방금 사용한 key'를 표시할 때 사용한다.
        """
        node = Node(data=data)
        node.next = self.head

        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node

        self.head = node
        self._size += 1
        return node

    def insert_back(self, data: Any) -> Node:
        """새 데이터를 tail 뒤에 넣고 생성된 노드를 반환한다."""
        node = Node(data=data)
        node.prev = self.tail

        if self.tail is not None:
            self.tail.next = node
        else:
            self.head = node

        self.tail = node
        self._size += 1
        return node

    def remove_front(self) -> Any | None:
        """head 노드를 제거하고 그 데이터를 반환한다."""
        if self.head is None:
            return None
        return self.remove_node(self.head)

    def remove_back(self) -> Any | None:
        """tail 노드를 제거하고 그 데이터를 반환한다.

        LRU 제거에서는 tail이 가장 오래 사용하지 않은 key이므로
        이 메서드가 메모리 초과 시 사용된다.
        """
        if self.tail is None:
            return None
        return self.remove_node(self.tail)

    def remove_node(self, node: Node) -> Any:
        """리스트 중간에 있는 특정 노드를 O(1)에 제거한다.

        해시맵이 key -> Node 참조를 가지고 있기 때문에, 삭제할 key의
        노드를 다시 검색하지 않고 바로 제거할 수 있다.
        """
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = None
        self._size -= 1
        return node.data

    def move_to_front(self, node: Node) -> None:
        """기존 노드를 head 위치로 옮긴다.

        GET이나 SET으로 key가 사용되면 가장 최근 사용 상태가 되므로
        해당 노드를 리스트 맨 앞으로 이동한다.
        """
        if node is self.head:
            return

        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = self.head

        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node

        self.head = node

