"""직접 만든 해시맵(HashMap).

파이썬 dict가 이미 해시맵이지만, 과제 목적상 내부 동작을 직접 구현했다.

한 줄 요약: 키(문자열)를 계산해서 서랍 번호를 뽑아내고, 그 서랍에 값을 넣는다.
그래서 "몇 번째에 있나" 세어보지 않고 한 번에 값을 꺼낼 수 있다(평균 O(1)).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Entry:
    """서랍 한 칸에 들어가는 항목 하나.

    같은 서랍에 여러 개가 들어갈 수 있어서(= 충돌), next로 다음 항목을 가리킨다.
    즉 서랍 안은 '연결 리스트(사슬)' 모양이 된다.
    """

    key: str
    value: Any
    next: Entry | None = None


class HashMap:
    """체이닝 방식으로 구현한 간단한 해시맵."""                                             

    def __init__(self, capacity: int = 4) -> None:
        # _buckets: 서랍장. 처음엔 8칸이고 전부 비어 있다(None).
        # _size: 지금 들어 있는 항목 개수.
        self._capacity = max(2, capacity)
        self._buckets: list[Entry | None] = [None] * self._capacity
        self._size = 0

    def size(self) -> int:
        """지금 담겨 있는 항목 개수."""

        return self._size

    def _hash(self, key: str) -> int:
        """문자열을 숫자로 바꾼다.

        글자를 하나씩 보면서 value * 31 + 글자코드 로 굴린다.
        31을 곱하는 이유는 글자 순서가 바뀌면 결과도 확 달라지게 하려는 것.
        ("ab"와 "ba"가 같은 숫자가 되면 안 되니까)
        마지막 & 0x7FFFFFFF는 값이 무한정 커지지 않게 잘라주는 역할.
        """

        value = 0
        for ch in key:
            value = (value * 31 + ord(ch)) & 0x7FFFFFFF
        return value

    def _index(self, key: str) -> int:
        """해시 숫자를 서랍 개수로 나눈 나머지 = 서랍 번호."""

        return self._hash(key) % self._capacity

    def _resize(self) -> None:
        """서랍장이 붐비면 칸 수를 2배로 늘리고 전부 다시 담는다.

        서랍 수는 그대로인데 항목만 늘어나면 사슬이 길어져서 느려진다.
        칸 수가 바뀌면 나머지 연산 결과도 바뀌므로 기존 항목을 다시 넣어야 한다.
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
        """키에 값을 저장한다. 같은 키가 이미 있으면 값만 바꾼다.

        순서
        1) 서랍이 75% 이상 차 있으면 먼저 크기를 늘린다
        2) 서랍 번호를 계산한다
        3) 그 서랍 사슬을 따라가며 같은 키가 있는지 본다 -> 있으면 값 교체
        4) 없으면 사슬 맨 앞에 새 항목을 끼워 넣는다
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
        """키로 값을 꺼낸다. 없으면 None.

        전체를 훑지 않고 해당 서랍 하나만 확인하므로 평균 O(1)이다.
        """

        current = self._buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def contains(self, key: str) -> bool:
        """키가 있는지만 확인한다(값은 필요 없을 때)."""

        current = self._buckets[self._index(key)]
        while current is not None:
            if current.key == key:
                return True
            current = current.next
        return False

    def keys(self) -> list[str]:
        """저장된 모든 키를 모아서 돌려준다.

        서랍장을 처음부터 끝까지 훑고 각 사슬도 따라가므로 O(n)이다.
        """

        result: list[str] = []
        for bucket in self._buckets:
            current = bucket
            while current is not None:
                result.append(current.key)
                current = current.next
        return result
