"""저장소(Repository): 브랜치 + HEAD + 사용자 + 그래프 + 역색인을 하나로 묶는 지휘자.

이 파일에는 '화면 출력'이 없다. 값을 돌려주거나 MiniGitError를 던질 뿐이다.
(문자열로 예쁘게 바꾸는 일은 cli.py가 한다 -> 로직과 화면의 분리)

Git 개념 3가지
- 브랜치 : 커밋 하나를 가리키는 이름표.  {"main": "c003", "feature": "c002"}
- HEAD   : '지금 올라타 있는 브랜치'를 가리키는 포인터.
- 커밋   : 현재 브랜치가 가리키는 커밋을 부모로 삼아 새 커밋을 만들고, 이름표를 새 커밋으로 옮긴다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from .graph import CommitGraph
from .index import InvertedIndex
from .models import Commit, HashGenerator, MiniGitError
from .sorting import merge_sort


def _now() -> datetime:
    """현재 시각(초 단위). 테스트에서는 가짜 시계로 바꿔 끼울 수 있다."""
    return datetime.now().replace(microsecond=0)


class Repository:
    """Mini Git 저장소 한 개."""

    def __init__(self, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or _now
        # hash 발급기는 INIT을 다시 해도 유지한다 -> hash가 세션 내내 유일하다
        self._hashes = HashGenerator()
        self._reset()

    def _reset(self) -> None:
        """저장소를 빈 상태로 되돌린다 (INIT 때 사용)."""
        self.initialized = False
        self.author = ""
        self.head = ""  # 현재 브랜치 이름
        self.branches: dict[str, str | None] = {}  # 브랜치 이름 -> 커밋 hash (첫 커밋 전엔 None)
        self.graph = CommitGraph()
        self.index = InvertedIndex()

    # ------------------------------------------------------------------
    # 저장소 / 브랜치 관리
    # ------------------------------------------------------------------
    def init(self, user_name: str) -> None:
        """INIT: 저장소 초기화. main 브랜치를 만들고 HEAD를 main으로, 작성자를 설정한다."""
        user_name = user_name.strip()
        if not user_name:
            raise MiniGitError("Invalid args")

        self._reset()
        self.initialized = True
        self.author = user_name
        self.head = "main"
        self.branches["main"] = None  # 아직 커밋이 없으므로 가리키는 곳이 없다

    def set_user(self, user_name: str) -> None:
        """USER: (보조 명령) 저장소는 그대로 두고 앞으로 만들 커밋의 작성자만 바꾼다.

        INIT은 저장소를 통째로 초기화하므로, 한 저장소에서 여러 사람의 커밋을 만들어
        작성자 검색/정렬을 보여 주려면 이 명령이 필요하다. (git config user.name 과 같은 역할)
        """
        self.require_init()
        user_name = user_name.strip()
        if not user_name:
            raise MiniGitError("Invalid args")
        self.author = user_name

    def create_branch(self, name: str) -> None:
        """BRANCH: 현재 HEAD가 가리키는 커밋에 새 이름표를 하나 더 단다.

        커밋을 복사하는 게 아니다. 같은 커밋을 가리키는 이름표가 하나 늘 뿐이다.
        첫 커밋 전에 만든 브랜치는 가리키는 곳이 None이고, 거기서 한 첫 커밋은 부모가 없다.
        (그래서 뿌리가 2개인 그래프도 만들 수 있고, 그때 PATH가 'No path'가 된다.)
        """
        self.require_init()
        if not name.strip():
            raise MiniGitError("Invalid args")
        if name in self.branches:
            raise MiniGitError(f"Branch already exists: {name}")
        self.branches[name] = self.branches[self.head]

    def switch(self, name: str) -> None:
        """SWITCH: HEAD를 다른 브랜치로 옮긴다. 커밋 데이터는 바뀌지 않는다."""
        self.require_init()
        if name not in self.branches:
            raise MiniGitError(f"Unknown branch: {name}")
        self.head = name

    def commit(self, message: str) -> Commit:
        """COMMIT: 현재 브랜치 끝을 부모로 하는 새 커밋을 만든다.

        순서
            1) 새 hash 발급, 부모 = 현재 브랜치가 가리키는 커밋 (없으면 부모 없음)
            2) 그래프(해시맵)에 저장
            3) 현재 브랜치 이름표를 새 커밋으로 이동
            4) 역색인(author / keyword) 갱신
        """
        self.require_init()
        if not message.strip():
            raise MiniGitError("Invalid args")

        tip = self.branches[self.head]
        commit = Commit(
            hash=self._hashes.next_hash(),
            message=message,
            author=self.author,
            timestamp=self._clock(),
            parents=[] if tip is None else [tip],
        )
        self.graph.add(commit)
        self.branches[self.head] = commit.hash
        self.index.add(commit)
        return commit

    # ------------------------------------------------------------------
    # 조회: 로그 / 탐색 / 검색
    # ------------------------------------------------------------------
    def log(self, sort_by: str | None = None) -> list[Commit]:
        """LOG: 커밋 목록.

        - 옵션 없음     : 위상 정렬 순서. 부모가 항상 자식보다 먼저 나온다.
        - sort_by=date  : timestamp 오름차순(오래된 것 먼저)
        - sort_by=author: 작성자 이름 오름차순(대소문자 무시)
        동률이면 '위상 정렬 순서'가 유지된다(병합 정렬이 안정 정렬이기 때문).
        """
        self.require_init()
        commits = [self.graph.get(h) for h in self.graph.topological_order()]

        if sort_by is None:
            return commits
        if sort_by == "date":
            return merge_sort(commits, key=lambda c: c.timestamp)
        if sort_by == "author":
            return merge_sort(commits, key=lambda c: c.author.lower())
        raise MiniGitError("Invalid args")

    def branch_labels(self) -> dict[str, list[str]]:
        """{커밋 hash: ["HEAD -> main", "feature"]}  로그에 붙일 브랜치 표시를 만든다."""
        labels: dict[str, list[str]] = {}
        for name, tip in self.branches.items():
            if tip is None:
                continue
            if name == self.head:
                labels.setdefault(tip, []).insert(0, f"HEAD -> {name}")  # 현재 브랜치는 맨 앞에
            else:
                labels.setdefault(tip, []).append(name)
        return labels

    def path(self, first: str, second: str) -> list[str] | None:
        """PATH: 두 커밋 사이 최단 경로. 길이 없으면 None."""
        self.require_init()
        start = self._resolve(first)
        end = self._resolve(second)
        return self.graph.shortest_path(start, end)

    def ancestors(self, commit_hash: str) -> list[Commit]:
        """ANCESTORS: 모든 조상 커밋(가까운 조상부터)."""
        self.require_init()
        target = self._resolve(commit_hash)
        return [self.graph.get(h) for h in self.graph.ancestors(target)]

    def search_keyword(self, keyword: str) -> list[Commit]:
        """SEARCH <keyword>: 역색인으로 후보를 바로 가져온다 (전체 순회 없음)."""
        self.require_init()
        if not keyword.strip():
            raise MiniGitError("Invalid args")
        return [self.graph.get(h) for h in self.index.search_keyword(keyword)]

    def search_author(self, name: str) -> list[Commit]:
        """SEARCH --author=<name>: 작성자 역색인 조회."""
        self.require_init()
        if not name.strip():
            raise MiniGitError("Invalid args")
        return [self.graph.get(h) for h in self.index.search_author(name)]

    # ------------------------------------------------------------------
    # 내부 도우미
    # ------------------------------------------------------------------
    def require_init(self) -> None:
        """INIT 전에는 다른 명령을 막는 공통 관문."""
        if not self.initialized:
            raise MiniGitError("Repository not initialized. Run INIT <user_name> first")

    def _resolve(self, commit_hash: str) -> str:
        """입력받은 hash를 확인한다. 없는 커밋이면 'Unknown commit: <입력>'.

        hash는 소문자로 발급되므로 입력은 대소문자를 가리지 않게 소문자로 맞춰 비교한다.
        """
        normalized = commit_hash.strip().lower()
        if normalized not in self.graph:
            raise MiniGitError(f"Unknown commit: {commit_hash}")
        return normalized
