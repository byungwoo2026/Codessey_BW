"""커밋 그래프(DAG)와 그래프 탐색 알고리즘.

그래프 용어 (이 파일을 읽기 위한 최소 지식)
- 노드(점)   : 커밋 하나
- 간선(선)   : 커밋 -> 부모 커밋 연결. commit.parents 에 적혀 있다
- 차수       : 한 노드에 붙은 선의 개수
- DAG        : 방향은 있고(자식 -> 부모), 돌아오는 길(순환)은 없는 그래프

왜 커밋 그래프는 DAG인가?
  커밋은 '이미 존재하는 커밋'만 부모로 가리킬 수 있다.
  부모는 항상 자식보다 먼저 만들어지므로 화살표는 과거 방향으로만 뻗는다.
  그래서 따라가다 제자리로 돌아오는 순환이 생길 수 없다.
  add()가 '부모가 이미 있어야 한다'를 검사하는 것이 이 보장을 코드로 만든 것이다.

이 파일의 알고리즘 3개
  topological_order : 부모가 항상 먼저 나오는 순서 (Kahn 알고리즘)
  ancestors         : 모든 조상 찾기                 (BFS)
  shortest_path     : 두 커밋 사이 최단 경로          (BFS)
셋 모두 시간복잡도 O(V + E)  (V=커밋 수, E=부모 연결 수)
"""

from __future__ import annotations

from .models import Commit


class CommitGraph:
    """커밋 저장소 + 커밋 그래프.

    내부 자료구조
    - _commits  : {hash: Commit}  해시맵(dict). hash로 커밋을 O(1)에 찾는다
    - _children : {hash: [자식 hash...]}  부모->자식 방향 역방향 연결
                  (Commit에는 부모만 적혀 있어서 자식 방향은 따로 기록해 둔다)
    - _order    : 만들어진 순서대로의 hash 목록
    """

    def __init__(self) -> None:
        self._commits: dict[str, Commit] = {}
        self._children: dict[str, list[str]] = {}
        self._order: list[str] = []

    # ------------------------------------------------------------------
    # 저장 / 조회
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._commits)

    def __contains__(self, commit_hash: str) -> bool:
        return commit_hash in self._commits

    def get(self, commit_hash: str) -> Commit | None:
        """hash로 커밋을 바로 꺼낸다. 없으면 None. (dict 조회라 평균 O(1))"""
        return self._commits.get(commit_hash)

    def add(self, commit: Commit) -> None:
        """커밋을 그래프에 추가한다.

        검사 두 가지가 DAG를 지켜 준다.
        1) hash 중복 금지 (커밋 hash는 유일해야 한다)
        2) 부모는 반드시 '이미 들어 있는' 커밋이어야 한다 -> 순환 불가능
        """
        if commit.hash in self._commits:
            raise ValueError(f"duplicate commit hash: {commit.hash}")
        if len(set(commit.parents)) != len(commit.parents):
            raise ValueError("duplicate parents")
        for parent in commit.parents:
            if parent not in self._commits:
                raise ValueError(f"unknown parent: {parent}")

        self._commits[commit.hash] = commit
        self._children[commit.hash] = []
        self._order.append(commit.hash)
        for parent in commit.parents:
            self._children[parent].append(commit.hash)

    # ------------------------------------------------------------------
    # 알고리즘 1: 위상 정렬 (LOG)
    # ------------------------------------------------------------------
    def topological_order(self) -> list[str]:
        """부모가 항상 자식보다 먼저 나오도록 모든 커밋 hash를 나열한다. (Kahn 알고리즘)

        핵심 아이디어: '아직 출력 안 된 부모가 0개'인 커밋부터 꺼낸다.
            1) 각 커밋의 "기다리는 부모 수"(진입 차수)를 센다
            2) 기다리는 부모가 0개인 커밋(= 뿌리 커밋)을 큐에 넣는다
            3) 큐에서 하나 꺼내 출력하고, 그 커밋의 자식들의 "기다리는 부모 수"를 1씩 줄인다
            4) 0이 된 자식은 이제 출력해도 되므로 큐에 넣는다
            5) 큐가 빌 때까지 반복
        부모가 2개인 커밋(병합 커밋)은 두 부모가 모두 나온 뒤에야 큐에 들어간다.

        시간복잡도 O(V + E). 순환이 있으면 일부 커밋이 영원히 0이 못 되어 빠지므로
        개수 비교로 순환을 감지할 수 있다(여기서는 일어날 수 없지만 안전장치).
        """
        waiting_parents = {h: len(self._commits[h].parents) for h in self._order}
        queue = [h for h in self._order if waiting_parents[h] == 0]

        front = 0  # 큐의 맨 앞 위치. pop(0)은 느리므로 위치 번호만 앞으로 민다
        while front < len(queue):
            current = queue[front]
            front += 1
            for child in self._children[current]:
                waiting_parents[child] -= 1
                if waiting_parents[child] == 0:
                    queue.append(child)

        if len(queue) != len(self._order):
            raise ValueError("cycle detected: not a DAG")
        return queue

    # ------------------------------------------------------------------
    # 알고리즘 2: 조상 탐색 (ANCESTORS)
    # ------------------------------------------------------------------
    def ancestors(self, commit_hash: str) -> list[str]:
        """commit_hash에서 부모 방향으로 도달 가능한 모든 조상을 가까운 순서로 돌려준다. (BFS)

        부모 -> 부모의 부모 -> ... 를 끝까지 거슬러 올라간다.
        visited(이미 본 커밋 집합)가 꼭 필요하다:
            병합 커밋처럼 같은 조상으로 가는 길이 여러 개일 때 중복 방문/중복 출력을 막는다.
        자기 자신은 조상이 아니므로 결과에 넣지 않는다.
        """
        visited = {commit_hash}
        queue = [commit_hash]
        found: list[str] = []

        front = 0
        while front < len(queue):
            current = queue[front]
            front += 1
            for parent in self._commits[current].parents:
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
                    found.append(parent)
        return found

    # ------------------------------------------------------------------
    # 알고리즘 3: 최단 경로 (PATH)
    # ------------------------------------------------------------------
    def neighbors(self, commit_hash: str) -> list[str]:
        """방향을 무시하고 이 커밋과 선으로 이어진 모든 커밋 = 부모 + 자식.

        PATH는 '부모-자식 연결을 무방향 간선으로 본다'고 정의돼 있다.
        갈라진 두 브랜치의 끝 커밋끼리는 공통 조상까지 내려갔다 올라가야 만나기 때문이다.
        """
        return self._commits[commit_hash].parents + self._children[commit_hash]

    def shortest_path(self, start: str, end: str) -> list[str] | None:
        """start -> end 최단 경로(간선 수 최소)를 돌려준다. 길이 없으면 None.

        최단 경로가 여러 개면 'h1->h2->...' 문자열이 사전순으로 가장 작은 경로를 고른다.

        방법 (2단계)
            1단계: end에서 BFS를 돌려 '모든 커밋의 end까지 거리'를 구한다.
            2단계: start에서 출발해, 매 걸음마다
                   '거리가 정확히 1 작은 이웃' 중 hash가 가장 작은 쪽으로 걷는다.

        왜 이 욕심쟁이(greedy) 선택이 맞나?
            최단 경로는 모두 같은 개수의 커밋을 지난다. 길이가 같은 두 문자열의 사전순 비교는
            '처음으로 달라지는 칸'이 결정하므로, 앞 칸부터 작은 hash를 고르면
            전체 문자열도 가장 작다. ("c1->" 처럼 '-'가 숫자보다 작아서 hash 길이가 달라도 같은 결론)
        시간복잡도 O(V + E).
        """
        distance_to_end = self._distances_from(end)
        if start not in distance_to_end:
            return None

        path = [start]
        current = start
        while current != end:
            best: str | None = None
            for neighbor in self.neighbors(current):
                if distance_to_end.get(neighbor) == distance_to_end[current] - 1:
                    if best is None or neighbor < best:
                        best = neighbor
            # distance_to_end[current] >= 1 이면 거리가 1 작은 이웃이 반드시 하나 이상 있다
            assert best is not None
            path.append(best)
            current = best
        return path

    def _distances_from(self, source: str) -> dict[str, int]:
        """source에서 무방향 BFS를 돌려 {커밋: source까지의 최소 간선 수}를 만든다.

        BFS는 '가까운 곳부터 한 겹씩' 넓혀 가므로 처음 닿은 거리가 곧 최단 거리다.
        source와 이어지지 않은 커밋은 결과에 아예 나오지 않는다.
        """
        distance = {source: 0}
        queue = [source]

        front = 0
        while front < len(queue):
            current = queue[front]
            front += 1
            for neighbor in self.neighbors(current):
                if neighbor not in distance:
                    distance[neighbor] = distance[current] + 1
                    queue.append(neighbor)
        return distance
