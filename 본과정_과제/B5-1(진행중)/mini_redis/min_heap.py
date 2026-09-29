"""직접 구현한 최소 힙 모듈.

TTL은 '가장 빨리 만료되는 key'를 자주 확인해야 한다. 최소 힙은
가장 작은 expire_at 값을 루트에 두므로, 다음에 만료될 key를 O(1)에
peek 하고, 제거는 O(log N)에 처리할 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HeapItem:
    """TTL 만료 관리를 위한 최소 힙 요소.

    expire_at은 time.time() 기준 만료 시각이고, key는 만료시킬 대상이다.
    """

    expire_at: float
    key: str


class MinHeap:
    """가장 빠른 만료 시간을 peek/pop 하기 위한 최소 힙.

    내부 저장은 리스트 하나로 한다. 부모/자식 위치는 인덱스 계산으로
    찾는다: parent=(i-1)//2, left=i*2+1, right=i*2+2.
    """

    def __init__(self) -> None:
        """빈 힙을 만든다."""
        self._items: list[HeapItem] = []

    def size(self) -> int:
        """힙에 들어 있는 요소 수를 반환한다."""
        return len(self._items)

    def push(self, item: HeapItem) -> None:
        """새 만료 정보를 힙에 넣는다.

        일단 배열 끝에 붙인 뒤 _heapify_up()으로 부모와 비교하며
        올바른 위치까지 끌어올린다.
        """
        self._items.append(item)
        self._heapify_up(len(self._items) - 1)

    def peek(self) -> HeapItem | None:
        """가장 빨리 만료될 요소를 제거하지 않고 확인한다."""
        if not self._items:
            return None
        return self._items[0]

    def pop(self) -> HeapItem | None:
        """가장 빨리 만료될 요소를 꺼낸다.

        루트를 꺼낸 뒤 마지막 요소를 루트로 올리고, _heapify_down()으로
        다시 최소 힙 조건을 만족하게 만든다.
        """
        if not self._items:
            return None

        root = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._heapify_down(0)
        return root

    def _is_less(self, left: HeapItem, right: HeapItem) -> bool:
        """left가 right보다 힙에서 더 앞에 와야 하는지 판단한다."""
        if left.expire_at == right.expire_at:
            return left.key < right.key
        return left.expire_at < right.expire_at

    def _heapify_up(self, index: int) -> None:
        """삽입 후 부모보다 작으면 위로 올린다."""
        while index > 0:
            parent = (index - 1) // 2
            if not self._is_less(self._items[index], self._items[parent]):
                break
            self._items[index], self._items[parent] = self._items[parent], self._items[index]
            index = parent

    def _heapify_down(self, index: int) -> None:
        """pop 후 자식보다 크면 아래로 내린다."""
        size = len(self._items)

        while True:
            left = index * 2 + 1
            right = index * 2 + 2
            smallest = index

            if left < size and self._is_less(self._items[left], self._items[smallest]):
                smallest = left
            if right < size and self._is_less(self._items[right], self._items[smallest]):
                smallest = right

            if smallest == index:
                break

            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest

