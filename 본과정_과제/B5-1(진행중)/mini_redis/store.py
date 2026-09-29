"""Mini Redis의 핵심 저장소 로직.

이 파일은 사용자가 입력한 Redis 스타일 명령이 실제로 어떤 자료구조를
건드리는지 조립한다. 값 저장은 HashMap, 최근 사용 순서는
DoublyLinkedList, 만료 시간은 HashMap + MinHeap 조합으로 관리한다.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from math import ceil

from .hashmap import HashMap
from .linked_list import DoublyLinkedList, Node
from .min_heap import HeapItem, MinHeap


@dataclass
class StoreEntry:
    """Mini Redis에 저장되는 문자열 값.

    지금 과제 범위는 Redis String 타입만 구현하므로 value는 문자열 하나다.
    """

    value: str


class MiniRedis:
    """Redis String 명령, LRU, TTL을 조합한 인메모리 저장소.

    각 자료구조의 역할:
    - _data: key -> StoreEntry 저장
    - _lru: 최근 사용 순서 저장, head가 최신이고 tail이 가장 오래됨
    - _lru_nodes: key -> LRU Node 저장, 리스트 노드를 O(1)에 찾기 위함
    - _expires: key -> expire_at 저장
    - _expire_heap: 가장 빠른 expire_at을 빠르게 찾기 위한 최소 힙
    """

    def __init__(self) -> None:
        """빈 Mini Redis 인스턴스를 만든다."""
        self._data = HashMap()
        self._lru = DoublyLinkedList()
        self._lru_nodes = HashMap()
        self._expires = HashMap()
        self._expire_heap = MinHeap()
        self._used_memory = 0
        self._maxmemory = 0
        self._evicted_keys = 0

    def set(self, key: str, value: str) -> str:
        """SET key value 명령을 처리한다.

        1. 이미 만료된 키를 먼저 정리한다.
        2. 단일 엔트리가 maxmemory보다 크면 저장하지 않고 OOM을 반환한다.
        3. 기존 키면 메모리 사용량에서 기존 값을 뺀다.
        4. 새 값을 저장하고 TTL을 초기화한다.
        5. LRU를 최신 사용 상태로 갱신한다.
        6. 메모리를 초과하면 tail부터 LRU 제거한다.
        """
        self._delete_expired_keys()

        new_size = self._entry_size(key, value)
        if self._maxmemory > 0 and new_size > self._maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        old_entry = self._data.get(key)
        if old_entry is not None:
            self._used_memory -= self._entry_size(key, old_entry.value)

        self._data.put(key, StoreEntry(value=value))
        self._used_memory += new_size
        self._expires.remove(key)
        self._touch_lru(key)
        self._evict_until_under_limit()
        return "OK"

    def get(self, key: str) -> str:
        """GET key 명령을 처리한다.

        만료된 키는 먼저 삭제하고 (nil)을 반환한다. 값 조회에 성공한
        경우에만 LRU를 갱신한다.
        """
        if self._delete_if_expired(key):
            return "(nil)"

        entry = self._data.get(key)
        if entry is None:
            return "(nil)"

        self._touch_lru(key)
        return f'"{entry.value}"'

    def delete(self, key: str) -> str:
        """DEL key 명령을 처리한다.

        삭제 시 데이터, TTL 정보, LRU 노드를 모두 함께 제거한다.
        """
        if self._delete_if_expired(key):
            return "(integer) 0"

        removed = self._remove_key(key)
        return "(integer) 1" if removed else "(integer) 0"

    def exists(self, key: str) -> str:
        """EXISTS key 명령을 처리한다."""
        if self._delete_if_expired(key):
            return "(integer) 0"
        return "(integer) 1" if self._data.contains(key) else "(integer) 0"

    def dbsize(self) -> str:
        """DBSIZE 명령을 처리한다.

        개수를 세기 전에 만료된 키를 정리해야 실제 남은 key 수가 맞다.
        """
        self._delete_expired_keys()
        return f"(integer) {self._data.size()}"

    def keys(self) -> list[str]:
        """KEYS 명령을 처리한다. 패턴 매칭은 과제 범위에서 제외한다."""
        self._delete_expired_keys()
        return self._data.keys()

    def expire(self, key: str, seconds: int) -> str:
        """EXPIRE key seconds 명령을 처리한다.

        힙에서 기존 만료 정보를 직접 찾아 지우지는 않는다. 대신 _expires에
        최신 expire_at만 저장하고, 힙에는 새 기록을 계속 넣는다. 나중에
        힙에서 꺼낼 때 _expires와 값이 다르면 오래된 기록으로 보고 버린다.
        이 방식을 lazy deletion이라고 한다.
        """
        if self._delete_if_expired(key):
            return "(integer) 0"
        if not self._data.contains(key):
            return "(integer) 0"
        if seconds <= 0:
            self._remove_key(key)
            return "(integer) 1"

        expire_at = time.time() + seconds
        self._expires.put(key, expire_at)
        self._expire_heap.push(HeapItem(expire_at=expire_at, key=key))
        return "(integer) 1"

    def ttl(self, key: str) -> str:
        """TTL key 명령을 처리한다.

        Redis 규칙처럼 key가 없으면 -2, key는 있지만 만료 시간이 없으면
        -1, 만료 시간이 있으면 남은 초를 반환한다.
        """
        if self._delete_if_expired(key):
            return "(integer) -2"
        if not self._data.contains(key):
            return "(integer) -2"

        expire_at = self._expires.get(key)
        if expire_at is None:
            return "(integer) -1"

        remain = ceil(expire_at - time.time())
        if remain < 0:
            remain = 0
        return f"(integer) {remain}"

    def set_maxmemory(self, maxmemory: int) -> str:
        """CONFIG SET maxmemory bytes 명령을 처리한다."""
        if maxmemory < 0:
            return "(error) ERR value is not an integer or out of range"

        self._maxmemory = maxmemory
        self._evict_until_under_limit()
        return "OK"

    def info_memory(self) -> list[str]:
        """INFO memory 명령을 처리한다."""
        self._delete_expired_keys()
        return [
            f"used_memory:{self._used_memory}",
            f"maxmemory:{self._maxmemory}",
            f"evicted_keys:{self._evicted_keys}",
        ]

    def _entry_size(self, key: str, value: str) -> int:
        """과제에서 정한 메모리 계산 공식."""
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _touch_lru(self, key: str) -> None:
        """key를 가장 최근에 사용한 상태로 만든다."""
        node = self._lru_nodes.get(key)
        if node is not None:
            self._lru.move_to_front(node)
            return

        node = self._lru.insert_front(key)
        self._lru_nodes.put(key, node)

    def _remove_key(self, key: str) -> bool:
        """key와 관련된 모든 내부 상태를 제거한다."""
        entry = self._data.remove(key)
        if entry is None:
            self._expires.remove(key)
            self._remove_lru_node(key)
            return False

        self._used_memory -= self._entry_size(key, entry.value)
        self._expires.remove(key)
        self._remove_lru_node(key)
        return True

    def _remove_lru_node(self, key: str) -> None:
        """key에 연결된 LRU 노드를 제거한다."""
        node = self._lru_nodes.remove(key)
        if node is not None:
            self._lru.remove_node(node)

    def _delete_if_expired(self, key: str) -> bool:
        """특정 key가 만료되었으면 삭제하고 True를 반환한다."""
        expire_at = self._expires.get(key)
        if expire_at is None:
            return False
        if expire_at > time.time():
            return False

        self._remove_key(key)
        return True

    def _delete_expired_keys(self) -> None:
        """현재 시각 기준으로 만료된 key들을 힙에서 꺼내 정리한다."""
        now = time.time()

        while True:
            item = self._expire_heap.peek()
            if item is None or item.expire_at > now:
                return

            self._expire_heap.pop()
            current_expire = self._expires.get(item.key)
            if current_expire is not None and current_expire == item.expire_at:
                self._remove_key(item.key)

    def _evict_until_under_limit(self) -> None:
        """used_memory가 maxmemory 이하가 될 때까지 LRU key를 제거한다."""
        if self._maxmemory <= 0:
            return

        while self._used_memory > self._maxmemory:
            key = self._lru.remove_back()
            if key is None:
                return

            node = self._lru_nodes.remove(key)
            if node is None:
                continue

            entry = self._data.remove(key)
            if entry is None:
                self._expires.remove(key)
                continue

            self._used_memory -= self._entry_size(key, entry.value)
            self._expires.remove(key)
            self._evicted_keys += 1

