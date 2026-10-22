"""직접 구현한 정렬 알고리즘 (병합 정렬, merge sort).

과제 규칙상 파이썬 내장 정렬 기능은 쓸 수 없어서 손으로 만들었다.

병합 정렬의 성질 (평가에서 자주 묻는 부분)
- 평균 시간복잡도  : O(n log n)
- 최악 시간복잡도  : O(n log n)   <- 입력이 어떤 순서든 똑같다
- 추가 메모리      : O(n)         <- 합칠 때 새 리스트가 필요하다
- 안정 정렬 여부   : 안정(stable)  <- 키가 같은 항목끼리는 원래 순서를 유지한다

왜 병합 정렬인가?
- 퀵 정렬은 평균은 빠르지만 최악이 O(n^2)이고 안정 정렬이 아니다.
- 로그에서는 '날짜가 같은 커밋들은 원래(부모 먼저) 순서 유지'가 자연스럽다.
  안정 정렬이면 그게 공짜로 해결된다.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def merge_sort(items: list[T], key: Callable[[T], Any] | None = None) -> list[T]:
    """items를 key 기준 오름차순으로 정렬한 '새 리스트'를 돌려준다. 원본은 안 건드린다.

    key는 '무엇을 기준으로 비교할지'를 알려주는 함수다.
    기준만 바꿔 끼우면 같은 정렬 코드로 날짜순/작성자순을 모두 처리할 수 있다.
        merge_sort(commits, key=lambda c: c.timestamp)      # 날짜 기준
        merge_sort(commits, key=lambda c: c.author.lower()) # 작성자 기준

    아이디어(분할 정복)
        1) 반으로 쪼갠다            [5, 2, 4, 1] -> [5, 2] [4, 1]
        2) 각각 정렬한다(재귀)       [2, 5]       [1, 4]
        3) 정렬된 두 조각을 합친다   [1, 2, 4, 5]
    조각 길이가 0~1이면 이미 정렬된 것이므로 그대로 돌려준다(재귀의 끝).
    """
    if key is None:
        key = _identity

    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    return _merge(left, right, key)


def _identity(value: T) -> T:
    """key를 안 주면 값 자체를 기준으로 쓴다."""
    return value


def _merge(left: list[T], right: list[T], key: Callable[[T], Any]) -> list[T]:
    """이미 정렬된 두 리스트를 하나로 합친다. 합치기가 병합 정렬의 핵심이다.

    양쪽 맨 앞 항목을 비교해서 더 작은 쪽을 꺼내 결과에 붙이기를 반복한다.

    안정 정렬이 되는 이유: 키가 같을 때(<=) '왼쪽'을 먼저 꺼낸다.
    왼쪽 조각은 원래 입력에서 앞쪽에 있던 항목들이라 동점자의 원래 순서가 유지된다.
    (여기를 < 로 바꾸면 불안정 정렬이 된다. 평가에서 묻기 좋은 포인트!)
    """
    merged: list[T] = []
    i = 0  # left에서 다음에 볼 위치
    j = 0  # right에서 다음에 볼 위치

    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # 한쪽이 바닥나면 남은 쪽은 이미 정렬돼 있으니 통째로 뒤에 붙인다
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
