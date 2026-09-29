"""직접 만든 정렬 알고리즘.

과제 규칙상 sorted()와 list.sort()를 쓸 수 없어서 merge sort를 손으로 구현했다.

merge sort를 고른 이유
- 시간복잡도가 평균/최악 모두 O(n log n)으로 안정적이다
  (퀵 정렬은 평균은 빠르지만 최악이 O(n^2))
- 안정 정렬이다. 값이 같으면 원래 순서를 유지한다
"""

from __future__ import annotations

from typing import Callable, TypeVar


T = TypeVar("T")


def merge_sort(items: list[T], compare: Callable[[T, T], int]) -> list[T]:
    """sorted(), list.sort()를 쓰지 않는 안정 merge sort.

    아이디어: 반으로 쪼개고 -> 각각 정렬하고 -> 정렬된 둘을 합친다.

    compare는 '비교 기준'을 밖에서 주입받는 부분이다.
    날짜순, 작성자순처럼 기준만 바꿔 끼우면 같은 정렬 코드를 재사용할 수 있다.
    규칙: 왼쪽이 먼저면 음수, 같으면 0, 오른쪽이 먼저면 양수를 돌려준다.

    원본 리스트는 건드리지 않고 새 리스트를 만들어 돌려준다.
    """

    if len(items) <= 1:
        return items[:]

    mid = len(items) // 2
    left = merge_sort(items[:mid], compare)
    right = merge_sort(items[mid:], compare)
    return _merge(left, right, compare)


def _merge(left: list[T], right: list[T], compare: Callable[[T, T], int]) -> list[T]:
    """이미 정렬된 두 리스트를 앞에서부터 비교하며 하나로 합친다.

    양쪽 맨 앞을 비교해서 작은 쪽을 먼저 넣기를 반복한다.
    비교 결과가 같을 때(0) 왼쪽을 먼저 넣기 때문에 안정 정렬이 된다.
    왼쪽은 원래 앞에 있던 조각이므로 동점자의 원래 순서가 그대로 유지된다.
    """

    result: list[T] = []
    left_index = 0
    right_index = 0

    # 1) 양쪽에 아직 남아 있는 동안은 하나씩 비교해서 작은 쪽을 넣는다
    while left_index < len(left) and right_index < len(right):
        if compare(left[left_index], right[right_index]) <= 0:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    # 2) 한쪽이 먼저 바닥나면, 남은 쪽은 이미 정렬돼 있으니 그대로 이어 붙인다
    while left_index < len(left):
        result.append(left[left_index])
        left_index += 1

    while right_index < len(right):
        result.append(right[right_index])
        right_index += 1

    return result
