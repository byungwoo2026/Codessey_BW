"""CLI(REPL): 입력 한 줄 -> 파싱 -> 실행 -> 출력 을 반복한다.

역할 분담
- 이 파일  : 문자열을 해석하고(파싱), 결과를 보기 좋은 문장으로 바꾼다(출력 형식)
- Repository: 실제 일을 한다. 잘못된 입력이면 MiniGitError를 던진다

흐름:  "COMMIT \"Add login\""  ->  tokenize  ->  ["COMMIT", "Add login"]
        -> 명령 이름 대문자 변환 -> 핸들러 함수 호출 -> 출력할 줄 목록 반환
"""

from __future__ import annotations

import shlex
from typing import Callable

from .models import Commit, MiniGitError
from .repository import Repository

PROMPT = "mini-git> "
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

HELP_LINES = [
    "Commands (case-insensitive; quote arguments that contain spaces):",
    '  INIT <user_name>                 e.g. INIT "Alice"',
    "  BRANCH <branch_name>             create a branch at HEAD",
    "  SWITCH <branch_name>             move HEAD to a branch",
    '  COMMIT <message>                 e.g. COMMIT "Add login feature"',
    "  LOG [--sort-by=date|author]      parents first (topological) unless sorted",
    "  PATH <commit1> <commit2>         shortest path (parent/child links are undirected)",
    "  ANCESTORS <commit_hash>          every ancestor of a commit",
    '  SEARCH <keyword>                 e.g. SEARCH "login"',
    "  SEARCH --author=<name>           commits written by <name>",
    "  USER <name>                      (extra) change the author without resetting the repo",
    "  INDEX                            show the inverted indexes (debug)",
    "  STATUS                           show user / branch / HEAD",
    "  HELP, EXIT (or QUIT)",
]


# ----------------------------------------------------------------------
# 1) 파싱
# ----------------------------------------------------------------------
def tokenize(line: str) -> list[str]:
    """한 줄을 '단어 목록'으로 자른다. 따옴표로 감싼 부분은 한 덩어리로 취급한다.

    COMMIT "Add login feature"  ->  ["COMMIT", "Add login feature"]
    따옴표를 열고 닫지 않으면 Invalid args.
    """
    try:
        return shlex.split(line)
    except ValueError:
        raise MiniGitError("Invalid args") from None


def _expect(args: list[str], count: int) -> None:
    """인자 개수가 정확히 count개인지 확인한다. 아니면 Invalid args."""
    if len(args) != count:
        raise MiniGitError("Invalid args")


# ----------------------------------------------------------------------
# 2) 출력 형식
# ----------------------------------------------------------------------
def format_log_entry(commit: Commit, labels: list[str]) -> list[str]:
    """LOG 한 항목 = 3줄.  hash / author / timestamp / message 가 모두 보인다."""
    when = commit.timestamp.strftime(TIME_FORMAT)
    tag = f" [{', '.join(labels)}]" if labels else ""
    parents = ", ".join(commit.parents) if commit.parents else "-"
    return [
        f"commit {commit.hash} ({commit.author}, {when}){tag}",
        f"    parents: {parents}",
        f"    {commit.message}",
    ]


def format_commit_list(header: str, commits: list[Commit]) -> list[str]:
    """검색/조상 결과처럼 '한 줄 목록' 형식. 예) - c002: Add login feature (Alice)"""
    lines = [header]
    for commit in commits:
        lines.append(f"- {commit.hash}: {commit.message} ({commit.author})")
    return lines


def _plural(count: int) -> str:
    return "commit" if count == 1 else "commits"


# ----------------------------------------------------------------------
# 3) 명령 핸들러: (저장소, 인자들) -> 출력할 줄 목록
# ----------------------------------------------------------------------
def _cmd_init(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    repo.init(args[0])
    return ["Initialized repository.", f"Current branch: {repo.head}", f"Current user: {repo.author}"]


def _cmd_user(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    repo.set_user(args[0])
    return [f"Current user: {repo.author}"]


def _cmd_branch(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    repo.create_branch(args[0])
    return [f"Created branch: {args[0]}"]


def _cmd_switch(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    repo.switch(args[0])
    return [f"Switched to branch: {args[0]}"]


def _cmd_commit(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    commit = repo.commit(args[0])
    return [f"[{repo.head} {commit.hash}] {commit.message}"]


def _cmd_log(repo: Repository, args: list[str]) -> list[str]:
    sort_by = None
    if len(args) == 1 and args[0].lower().startswith("--sort-by="):
        sort_by = args[0].split("=", 1)[1].lower()
    elif args:
        raise MiniGitError("Invalid args")

    commits = repo.log(sort_by)
    if not commits:
        return ["No commits yet"]

    labels = repo.branch_labels()
    lines: list[str] = []
    for commit in commits:
        lines.extend(format_log_entry(commit, labels.get(commit.hash, [])))
    return lines


def _cmd_path(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 2)
    path = repo.path(args[0], args[1])
    if path is None:
        return ["No path"]
    return ["Path: " + " -> ".join(path)]


def _cmd_ancestors(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    found = repo.ancestors(args[0])
    if not found:
        return ["No ancestors"]
    return format_commit_list(f"Ancestors of {args[0].lower()} ({len(found)}):", found)


def _cmd_search(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 1)
    query = args[0]
    if query.lower().startswith("--author="):
        found = repo.search_author(query.split("=", 1)[1])
    elif query.startswith("--"):
        raise MiniGitError("Invalid args")  # 모르는 옵션
    else:
        found = repo.search_keyword(query)

    if not found:
        return ["No commits found"]
    return format_commit_list(f"Found {len(found)} {_plural(len(found))}:", found)


def _cmd_index(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 0)
    repo.require_init()
    return repo.index.dump()


def _cmd_status(repo: Repository, args: list[str]) -> list[str]:
    _expect(args, 0)
    repo.require_init()
    tip = repo.branches[repo.head] or "(no commits yet)"
    return [f"User: {repo.author}", f"Current branch: {repo.head}", f"HEAD commit: {tip}",
            f"Branches: {', '.join(repo.branches)}", f"Total commits: {len(repo.graph)}"]


def _cmd_help(repo: Repository, args: list[str]) -> list[str]:
    return list(HELP_LINES)


Handler = Callable[[Repository, list[str]], list[str]]

# 명령 이름 -> 처리 함수.  새 명령은 여기에 한 줄 추가하면 된다.
COMMANDS: dict[str, Handler] = {
    "INIT": _cmd_init,
    "USER": _cmd_user,
    "BRANCH": _cmd_branch,
    "SWITCH": _cmd_switch,
    "COMMIT": _cmd_commit,
    "LOG": _cmd_log,
    "PATH": _cmd_path,
    "ANCESTORS": _cmd_ancestors,
    "SEARCH": _cmd_search,
    "INDEX": _cmd_index,
    "STATUS": _cmd_status,
    "HELP": _cmd_help,
}


# ----------------------------------------------------------------------
# 4) 실행 / REPL
# ----------------------------------------------------------------------
def execute(repo: Repository, line: str) -> list[str] | None:
    """한 줄을 실행하고 출력할 줄 목록을 돌려준다. EXIT/QUIT이면 None(= 종료 신호).

    MiniGitError는 여기서 잡아서 '에러 문장 한 줄'로 바꾼다. 프로그램은 죽지 않는다.
    """
    try:
        tokens = tokenize(line)
        if not tokens:
            return []  # 빈 줄은 무시

        name = tokens[0].upper()  # 명령어는 대소문자 구분 없음
        if name in ("EXIT", "QUIT"):
            return None
        handler = COMMANDS.get(name)
        if handler is None:
            return [f"Unknown command: {tokens[0]}"]
        return handler(repo, tokens[1:])
    except MiniGitError as error:
        return [str(error)]


def run_repl(repo: Repository | None = None,
             read: Callable[[str], str] = input,
             write: Callable[[str], None] = print) -> None:
    """프롬프트를 띄우고 명령을 계속 받는 반복문 (Read-Eval-Print Loop).

    저장소는 한 번만 만들어 계속 쓰므로 앞에서 만든 커밋/브랜치가 유지된다.
    EXIT, QUIT, Ctrl+D(EOF), Ctrl+C 모두 조용히 종료한다.
    read/write를 바꿔 끼울 수 있게 해 둔 것은 테스트를 쉽게 하기 위해서다.
    """
    repo = repo or Repository()
    write("Mini Git - type HELP for commands, EXIT to quit.")

    while True:
        try:
            line = read(PROMPT)
        except (EOFError, KeyboardInterrupt):
            write("")
            return

        output = execute(repo, line)
        if output is None:
            return
        for text in output:
            write(text)
