"""Mini Git의 핵심 두뇌.

여기서 세 가지를 동시에 관리한다.

1) 커밋 그래프 : 커밋 노드들과 parents 연결. LOG / PATH / ANCESTORS의 재료
2) 브랜치      : 브랜치 이름 -> 그 브랜치가 가리키는 커밋 hash
3) 검색 인덱스 : 단어/작성자 -> 커밋 hash 목록 (역색인)

세 가지 모두 직접 만든 HashMap에 담는다.
그래야 이름표(문자열)로 실제 데이터를 한 번에 꺼낼 수 있기 때문이다.
"""

from __future__ import annotations

from datetime import datetime

from .hashmap import HashMap
from .models import Commit
from .sorting import merge_sort


class MiniGit:
    """브랜치, 커밋 그래프, 검색 인덱스를 관리하는 핵심 클래스."""

    def __init__(self) -> None:
        # initialized    : INIT을 했는지 여부. 안 했으면 다른 명령은 막는다
        # author         : 현재 사용자 이름. 커밋을 만들 때 기록한다
        # head_branch    : 지금 올라타 있는 브랜치 이름 (= HEAD)
        # _counter       : 커밋 hash를 만들 때 쓰는 일련번호
        # _commits       : hash -> Commit 객체 (그래프의 노드 저장소)
        # _branches      : 브랜치 이름 -> 커밋 hash
        # _commit_order  : 커밋이 만들어진 순서. LOG의 출력 순서로 쓴다
        # _keyword_index : 단어 -> 커밋 hash 목록 (역색인)
        # _author_index  : 작성자 -> 커밋 hash 목록 (역색인)
        self.initialized = False
        self.author = ""
        self.head_branch = ""
        self._counter = 0
        self._commits = HashMap()
        self._branches = HashMap()
        self._commit_order: list[str] = []
        self._keyword_index = HashMap()
        self._author_index = HashMap()

    def init(self, user_name: str) -> list[str]:
        """INIT <user_name> - 저장소를 새로 만든다.

        main 브랜치를 만들고 HEAD를 main으로 맞춘 뒤 사용자 이름을 기억한다.
        아직 커밋이 없으므로 main이 가리키는 값은 None이다.
        """

        if not user_name:
            return ["Invalid args"]

        # 이미 쓰던 저장소가 있어도 전부 초기 상태로 되돌린다
        self.__init__()
        self.initialized = True
        self.author = user_name
        self.head_branch = "main"
        self._branches.put("main", None)
        return [f"Initialized repository for {user_name}", "Current branch: main"]

    def branch(self, branch_name: str) -> list[str]:
        """BRANCH <name> - 지금 HEAD가 가리키는 커밋에서 새 브랜치를 만든다.

        커밋을 복사하는 게 아니라 같은 커밋을 가리키는 이름표를 하나 더 다는 것이다.
        여기서부터 커밋하면 그래프가 갈라진다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not branch_name:
            return ["Invalid args"]
        if self._branches.contains(branch_name):
            return [f"Branch already exists: {branch_name}"]

        self._branches.put(branch_name, self._current_head())
        return [f"Created branch: {branch_name}"]

    def switch(self, branch_name: str) -> list[str]:
        """SWITCH <name> - HEAD를 다른 브랜치로 옮긴다.

        커밋 데이터는 그대로고, 지금 어디에 서 있는지만 바뀐다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not self._branches.contains(branch_name):
            return [f"Unknown branch: {branch_name}"]

        self.head_branch = branch_name
        return [f"Switched to branch: {branch_name}"]

    def commit(self, message: str) -> list[str]:
        """COMMIT <message> - 지금 HEAD를 부모로 삼는 새 커밋을 만든다.

        하는 일이 네 가지다.
        1) 새 커밋 노드를 만든다 (부모 = 현재 HEAD가 가리키는 커밋)
        2) hash -> 커밋 으로 저장하고, 만든 순서도 기록한다
        3) 현재 브랜치가 새 커밋을 가리키도록 옮긴다
        4) 검색 인덱스(역색인)를 갱신한다

        첫 커밋은 부모가 없어서 parents가 빈 리스트가 된다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not message:
            return ["Invalid args"]

        parent = self._current_head()
        parents = [] if parent is None else [parent]
        commit_hash = self._next_hash()
        commit = Commit(
            hash=commit_hash,
            message=message,
            author=self.author,
            timestamp=datetime.now().isoformat(timespec="seconds"),
            parents=parents,
        )

        self._commits.put(commit.hash, commit)
        self._commit_order.append(commit.hash)
        self._branches.put(self.head_branch, commit.hash)
        self._add_to_indexes(commit)
        return [f"Committed {commit.hash}: {commit.message}"]

    def log(self, sort_by: str | None = None) -> list[str]:
        """LOG - 커밋 목록을 출력한다.

        옵션이 없으면 만들어진 순서(_commit_order) 그대로 출력한다.
        부모는 항상 자식보다 먼저 만들어지므로, 이 순서는 자연스럽게
        부모가 자식보다 먼저 나오는 위상 정렬 순서를 만족한다.

        --sort-by=date   : 시간순
        --sort-by=author : 작성자 이름순
        정렬은 직접 만든 merge_sort에 비교 함수만 바꿔 끼워서 처리한다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]

        commits = self._all_commits()
        if not commits:
            return ["No commits"]

        if sort_by == "date":
            commits = merge_sort(commits, _compare_by_date)
        elif sort_by == "author":
            commits = merge_sort(commits, _compare_by_author)
        elif sort_by is not None:
            return ["Invalid args"]

        return [_format_commit(commit) for commit in commits]

    def search_keyword(self, keyword: str) -> list[str]:
        """SEARCH <keyword> - 메시지에 그 단어가 들어간 커밋을 찾는다.

        커밋을 전부 훑지 않는다. 커밋할 때 미리 만들어 둔
        단어 -> 커밋 목록 서랍에서 바로 꺼낸다. 이게 역색인이다.
        전체 순회는 O(전체 커밋 수)지만 역색인 조회는 평균 O(1)이다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not keyword:
            return ["Invalid args"]

        hashes = self._keyword_index.get(keyword.lower())
        return self._format_hashes(hashes)

    def search_author(self, author: str) -> list[str]:
        """SEARCH --author=<name> - 특정 사람이 쓴 커밋을 찾는다.

        방식은 키워드 검색과 같고, 보는 서랍만 작성자 인덱스로 바뀐다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not author:
            return ["Invalid args"]

        hashes = self._author_index.get(author.lower())
        return self._format_hashes(hashes)

    def ancestors(self, commit_hash: str) -> list[str]:
        """ANCESTORS <hash> - 그 커밋의 모든 조상을 찾는다.

        부모 방향으로만 계속 거슬러 올라가는 그래프 탐색(DFS)이다.

        진행 방식
        - stack에 아직 안 가본 조상들을 쌓아 두고 하나씩 꺼낸다
        - 꺼낸 커밋의 부모들을 다시 stack에 넣는다
        - 이미 결과에 있는 커밋은 건너뛴다 (합쳐진 갈래에서 중복 방문 방지)
        - stack이 빌 때까지 반복하면 빠짐없이 모두 방문하게 된다
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not self._commits.contains(commit_hash):
            return [f"Unknown commit: {commit_hash}"]

        result: list[str] = []
        stack: list[str] = []
        commit = self._commits.get(commit_hash)
        for parent in commit.parents:
            stack.append(parent)

        while stack:
            current_hash = stack.pop()
            if _contains(result, current_hash):
                continue
            result.append(current_hash)

            current_commit = self._commits.get(current_hash)
            if current_commit is not None:
                for parent in current_commit.parents:
                    stack.append(parent)

        if not result:
            return ["No ancestors"]
        return result

    def path(self, start: str, end: str) -> list[str]:
        """PATH <c1> <c2> - 두 커밋 사이 최단 경로를 출력한다.

        여기서는 부모/자식 연결을 방향 없는 선으로 본다.
        서로 다른 브랜치의 두 커밋은 공통 조상까지 내려갔다가 다시 올라가야
        만날 수 있기 때문이다.

        최단 경로가 여러 개면 a->b->c 형태의 문자열로 만들었을 때
        사전순으로 가장 작은 것을 고른다.
        """

        if not self._is_ready():
            return ["Repository not initialized"]
        if not self._commits.contains(start):
            return [f"Unknown commit: {start}"]
        if not self._commits.contains(end):
            return [f"Unknown commit: {end}"]
        if start == end:
            return [start]

        found_paths = self._shortest_paths(start, end)
        if not found_paths:
            return ["No path"]

        ordered = merge_sort(found_paths, _compare_path_text)
        return ["->".join(ordered[0])]

    def _is_ready(self) -> bool:
        """INIT을 마쳤는지 확인한다. 모든 명령의 공통 관문."""

        return self.initialized

    def _current_head(self) -> str | None:
        """지금 브랜치가 가리키는 커밋 hash. 커밋이 하나도 없으면 None."""

        return self._branches.get(self.head_branch)

    def _next_hash(self) -> str:
        """겹치지 않는 새 커밋 hash를 만든다.

        일련번호를 1씩 올려 C000001, C000002 형태로 만든다.
        혹시라도 이미 쓰인 번호면 다음 번호로 넘어가므로 중복이 생기지 않는다.
        """

        while True:
            self._counter += 1
            commit_hash = f"C{self._counter:06d}"
            if not self._commits.contains(commit_hash):
                return commit_hash

    def _add_to_indexes(self, commit: Commit) -> None:
        """커밋 하나를 역색인에 등록한다.

        - 작성자 인덱스: 작성자 이름을 소문자로 바꿔 키로 쓴다
        - 키워드 인덱스: 메시지를 공백으로 쪼개고 소문자로 바꿔 각각 키로 쓴다

        검색할 때 훑지 않으려면 저장할 때 미리 정리해 두어야 한다.
        검색을 빠르게 만드는 비용을 커밋 시점으로 옮긴 셈이다.
        """

        self._add_index_value(self._author_index, commit.author.lower(), commit.hash)
        for token in commit.message.split():
            normalized = token.lower()
            if normalized:
                self._add_index_value(self._keyword_index, normalized, commit.hash)

    def _add_index_value(self, index: HashMap, key: str, commit_hash: str) -> None:
        """인덱스의 특정 키에 커밋 hash를 덧붙인다.

        그 키가 처음이면 빈 목록을 만들어 넣고, 이미 있으면 뒤에 추가한다.
        같은 단어가 메시지에 두 번 나와도 중복으로 쌓이지 않게 걸러 준다.
        """

        values = index.get(key)
        if values is None:
            values = []
            index.put(key, values)
        if not _contains(values, commit_hash):
            values.append(commit_hash)

    def _all_commits(self) -> list[Commit]:
        """만들어진 순서대로 커밋 객체를 모아서 돌려준다.

        _commit_order에는 hash만 들어 있으므로 해시맵으로 실제 객체를 꺼낸다.
        """

        result: list[Commit] = []
        for commit_hash in self._commit_order:
            commit = self._commits.get(commit_hash)
            if commit is not None:
                result.append(commit)
        return result

    def _format_hashes(self, hashes: list[str] | None) -> list[str]:
        """검색 결과(hash 목록)를 사람이 읽는 문장으로 바꾼다."""

        if not hashes:
            return ["No commits"]

        commits: list[Commit] = []
        for commit_hash in hashes:
            commit = self._commits.get(commit_hash)
            if commit is not None:
                commits.append(commit)

        if not commits:
            return ["No commits"]
        return [_format_commit(commit) for commit in commits]

    def _shortest_paths(self, start: str, end: str) -> list[list[str]]:
        """BFS로 start에서 end까지 가는 최단 경로들을 모두 찾는다.

        BFS는 가까운 곳부터 차례로 넓혀 가므로, 목적지에 처음 닿은 깊이가
        곧 최단 거리다.

        - queue          : 아직 살펴볼 경로들. 지나온 길 전체를 통째로 담는다
        - visited_depths : 각 커밋에 몇 걸음 만에 닿았는지 기록
        - found_depth    : 목적지에 처음 닿은 깊이. 이보다 깊어지면 탐색을 멈춘다

        같은 길이의 경로가 여러 개일 수 있으므로 하나 찾아도 바로 끝내지 않고,
        같은 깊이까지는 계속 모아서 목록으로 돌려준다.
        """

        queue: list[list[str]] = [[start]]
        visited_depths: list[tuple[str, int]] = [(start, 0)]
        found_paths: list[list[str]] = []
        found_depth: int | None = None
        queue_index = 0

        while queue_index < len(queue):
            path = queue[queue_index]
            queue_index += 1
            current = path[-1]
            depth = len(path) - 1

            # 최단 거리보다 길어졌으면 더 볼 필요가 없다
            if found_depth is not None and depth > found_depth:
                break
            if current == end:
                found_depth = depth
                found_paths.append(path)
                continue

            for neighbor in self._neighbors(current):
                # 왔던 길을 다시 밟으면 빙빙 돌게 되므로 제외한다
                if _contains(path, neighbor):
                    continue
                next_depth = depth + 1
                previous_depth = _visited_depth(visited_depths, neighbor)
                # 더 짧게 도달한 적이 있으면 이 경로는 최단이 될 수 없다
                if previous_depth is not None and previous_depth < next_depth:
                    continue
                if previous_depth is None:
                    visited_depths.append((neighbor, next_depth))
                queue.append(path + [neighbor])

        return found_paths

    def _neighbors(self, commit_hash: str) -> list[str]:
        """이 커밋과 선으로 이어진 커밋들(부모 + 자식)을 모은다.

        부모는 commit.parents에 적혀 있어서 바로 알 수 있다.
        자식은 반대로 나를 부모로 적어 둔 커밋을 찾아야 해서 전체를 훑는다.

        PATH가 방향을 무시하고 최단 경로를 찾을 수 있는 이유가 여기에 있다.
        결과를 hash 사전순으로 정렬해 두면, 같은 길이의 경로 중 사전순으로
        작은 경로가 먼저 발견된다.
        """

        result: list[str] = []
        commit = self._commits.get(commit_hash)
        if commit is not None:
            for parent in commit.parents:
                if not _contains(result, parent):
                    result.append(parent)

        for other_hash in self._commit_order:
            other = self._commits.get(other_hash)
            if other is not None and _contains(other.parents, commit_hash):
                if not _contains(result, other.hash):
                    result.append(other.hash)

        return merge_sort(result, _compare_text)


def _format_commit(commit: Commit) -> str:
    """커밋 한 줄 출력 형식. 부모가 없으면 - 로 표시한다."""

    parents = ",".join(commit.parents) if commit.parents else "-"
    return f"{commit.hash} | {commit.author} | {commit.timestamp} | parents={parents} | {commit.message}"


def _compare_text(left: str, right: str) -> int:
    """문자열 두 개를 사전순으로 비교한다. 앞서면 -1, 같으면 0, 뒤면 1."""

    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def _compare_path_text(left: list[str], right: list[str]) -> int:
    """경로를 a->b->c 형태의 문자열로 만들어 사전순 비교한다.

    최단 경로가 여러 개일 때 어떤 것을 고를지 정하는 규칙.
    """

    return _compare_text("->".join(left), "->".join(right))


def _compare_by_date(left: Commit, right: Commit) -> int:
    """시간순 비교. 시간이 같으면 hash로 순서를 정해 결과가 흔들리지 않게 한다."""

    date_result = _compare_text(left.timestamp, right.timestamp)
    if date_result != 0:
        return date_result
    return _compare_text(left.hash, right.hash)


def _compare_by_author(left: Commit, right: Commit) -> int:
    """작성자 이름순 비교. 대소문자를 무시하고, 같으면 hash로 순서를 정한다."""

    author_result = _compare_text(left.author.lower(), right.author.lower())
    if author_result != 0:
        return author_result
    return _compare_text(left.hash, right.hash)


def _contains(items: list, value: object) -> bool:
    """리스트 안에 값이 있는지 직접 확인한다(in 대신 손으로 구현한 버전)."""

    for item in items:
        if item == value:
            return True
    return False


def _visited_depth(items: list[tuple[str, int]], commit_hash: str) -> int | None:
    """그 커밋에 몇 걸음 만에 닿았는지 찾아본다. 아직이면 None."""

    for item_hash, depth in items:
        if item_hash == commit_hash:
            return depth
    return None
