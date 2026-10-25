"""직접 구현한 해시맵 모듈.

이 과제에서는 Python의 dict로 key-value 저장소를 대체하면 안 된다.
그래서 고정 길이 버킷 배열(list)을 만들고, 같은 버킷에 들어온 값은
Entry 노드를 연결하는 체이닝 방식으로 충돌을 처리한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Entry:
    """해시 버킷 안에서 체이닝으로 연결되는 엔트리.

    key와 value를 한 쌍으로 저장하고, next는 같은 버킷에 연결된
    다음 엔트리를 가리킨다. 즉, 충돌이 나면 연결 리스트처럼 이어진다.
    """

    key: str
    value: Any
    next: Entry | None = None


class HashMap:
    """dict를 대신하는 체이닝 방식 해시맵.

    버킷 위치는 직접 만든 _hash() 결과로 결정한다. 데이터가 많아져
    로드 팩터가 0.75를 넘으면 버킷 수를 2배로 늘려 검색 성능이
    급격히 나빠지지 않게 한다.
    """

    def __init__(self, capacity: int = 8) -> None:
        """초기 버킷 배열을 만든다.

        _buckets는 Entry 또는 None을 담는 리스트다. 각 칸이 하나의
        버킷이고, 충돌된 Entry들은 next로 이어진다.
        """
        self._capacity = max(2, capacity)
        self._buckets: list[Entry | None] = [None] * self._capacity
        self._size = 0

    def size(self) -> int:
        """현재 저장된 key 개수를 반환한다."""
        return self._size

    def _hash(self, key: str) -> int:
        """문자열 key를 정수 해시값으로 바꾼다.

        31을 곱하며 누적하는 단순 다항 해시 방식이다. 같은 key는 항상
        같은 값을 만들고, 다른 key는 가능한 한 다른 값이 나오게 한다.
        """
        value = 0
        for ch in key:
            value = (value * 31 + ord(ch)) & 0x7FFFFFFF
        return value

    def _index(self, key: str) -> int:
        """해시값을 현재 버킷 범위 안의 인덱스로 바꾼다."""
        return self._hash(key) % self._capacity

    def _resize(self) -> None:
        """버킷 수를 2배로 늘리고 모든 Entry를 다시 배치한다.

        capacity가 바뀌면 key % capacity 결과도 달라질 수 있으므로,
        기존 Entry를 새 버킷 배열 기준으로 다시 put 해야 한다.
        """
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [None] * self._capacity
        old_size = self._size
        self._size = 0

        for bucket in old_buckets:
            current = bucket
            while current is not None:
                self.put(current.key, current.value)
                current = current.next

        self._size = old_size

    def put(self, key: str, value: Any) -> None:
        """key에 value를 저장한다.

        이미 같은 key가 있으면 값을 덮어쓰고, 없으면 해당 버킷의
        맨 앞에 새 Entry를 연결한다.
        """
        if (self._size + 1) / self._capacity > 0.75:
            self._resize()

        index = self._index(key)
        current = self._buckets[index]

        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next

        self._buckets[index] = Entry(key=key, value=value, next=self._buckets[index])
        self._size += 1

    def get(self, key: str) -> Any | None:
        """key에 해당하는 값을 찾는다. 없으면 None을 반환한다."""
        current = self._buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def contains(self, key: str) -> bool:
        """key가 존재하는지 True/False로 확인한다."""
        current = self._buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return True
            current = current.next
        return False

    def remove(self, key: str) -> Any | None:
        """key를 삭제하고 삭제된 값을 반환한다.

        체이닝 중간의 Entry를 지울 수 있으므로 previous 포인터를 같이
        들고 다니면서 앞 노드와 뒤 노드를 다시 연결한다.
        """
        index = self._index(key)
        current = self._buckets[index]
        previous: Entry | None = None

        while current is not None:
            if current.key == key:
                if previous is None:
                    self._buckets[index] = current.next
                else:
                    previous.next = current.next
                self._size -= 1
                return current.value

            previous = current
            current = current.next

        return None

    def keys(self) -> list[str]:
        """현재 저장된 모든 key를 리스트로 모아 반환한다."""
        result: list[str] = []
        for bucket in self._buckets:
            current = bucket
            while current is not None:
                result.append(current.key)
                current = current.next
        return result

