"""사용자 입력을 받아 처리하는 창구(CLI).

mini-git> 프롬프트를 띄우고, 사용자가 친 한 줄을 해석해서
MiniGit(repository.py)의 알맞은 기능을 호출한 뒤 결과를 화면에 뿌린다.

여기서는 계산을 하지 않는다. 입력 검사와 전달만 담당한다.
그래야 로직(repository.py)과 화면(cli.py)이 분리돼서 고치기 쉬워진다.
"""

from __future__ import annotations

import shlex

from .repository import MiniGit


def run_command(repo: MiniGit, line: str) -> list[str] | None:
    """한 줄짜리 명령을 해석해서 실행하고, 출력할 문장 목록을 돌려준다.

    돌려주는 값의 의미
    - list : 화면에 출력할 문장들
    - None : 프로그램을 끝내라는 뜻 (exit / quit)

    shlex.split을 쓰는 이유는 따옴표 처리 때문이다.
    COMMIT "Add login feature" 를 세 조각이 아니라
    ["COMMIT", "Add login feature"] 두 조각으로 잘라 준다.
    따옴표를 닫지 않으면 오류가 나므로 Invalid args로 처리한다.
    """

    try:
        parts = shlex.split(line)
    except ValueError:
        return ["Invalid args"]

    if not parts:
        return []

    # 명령어는 대소문자를 가리지 않으므로 대문자로 통일해서 비교한다
    command = parts[0].upper()
    if command in ("EXIT", "QUIT"):
        return None

    # 아래 명령들은 모두 "인자 개수 확인 -> repo에 전달" 구조로 똑같다
    if command == "INIT":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.init(parts[1])

    if command == "BRANCH":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.branch(parts[1])

    if command == "SWITCH":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.switch(parts[1])

    if command == "COMMIT":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.commit(parts[1])

    # LOG와 SEARCH는 옵션이 붙을 수 있어서 따로 함수로 뺐다
    if command == "LOG":
        return _run_log(repo, parts)

    if command == "PATH":
        if len(parts) != 3:
            return ["Invalid args"]
        return repo.path(parts[1], parts[2])

    if command == "ANCESTORS":
        if len(parts) != 2:
            return ["Invalid args"]
        return repo.ancestors(parts[1])

    if command == "SEARCH":
        return _run_search(repo, parts)

    return [f"Unknown command: {parts[0]}"]


def repl() -> int:
    """입력 -> 실행 -> 출력을 계속 반복하는 반복문(REPL).

    저장소(repo)를 한 번만 만들고 계속 재사용하기 때문에
    이전에 만든 커밋과 브랜치가 그대로 남아 있다.

    Ctrl+C(KeyboardInterrupt)나 Ctrl+D(EOFError)로도 조용히 끝낼 수 있다.
    """

    repo = MiniGit()

    while True:
        try:
            line = input("mini-git> ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 0

        output = run_command(repo, line)
        if output is None:
            return 0
        for row in output:
            print(row)


def main() -> int:
    """main.py가 호출하는 시작 함수."""

    return repl()


def _run_log(repo: MiniGit, parts: list[str]) -> list[str]:
    """LOG 명령의 옵션을 해석한다.

    LOG                -> 기본 출력
    LOG --sort-by=date -> = 뒤의 date만 떼어내서 repo.log에 넘긴다
    그 외 형태는 전부 Invalid args
    """

    if len(parts) == 1:
        return repo.log()
    if len(parts) == 2 and parts[1].startswith("--sort-by="):
        sort_by = parts[1].split("=", 1)[1]
        return repo.log(sort_by=sort_by)
    return ["Invalid args"]


def _run_search(repo: MiniGit, parts: list[str]) -> list[str]:
    """SEARCH 명령의 옵션을 해석한다.

    --author= 로 시작하면 작성자 검색, 아니면 키워드 검색으로 보낸다.
    split("=", 1)은 이름에 =가 들어 있어도 첫 번째 =에서만 자르기 위함이다.
    """

    if len(parts) != 2:
        return ["Invalid args"]

    query = parts[1]
    if query.startswith("--author="):
        author = query.split("=", 1)[1]
        return repo.search_author(author)

    return repo.search_keyword(query)
