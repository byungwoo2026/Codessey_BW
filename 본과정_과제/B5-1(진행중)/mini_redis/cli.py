"""Mini Redis CLI 모듈.

사용자가 터미널에서 입력한 한 줄 명령을 파싱하고, MiniRedis 저장소에
전달한 뒤 Redis 스타일 문자열로 출력한다. 실행 모드는 두 가지다.

1. 인자 없이 실행: mini-redis> 프롬프트가 반복되는 REPL 모드
2. 인자와 함께 실행: 한 번만 명령을 실행하고 종료하는 단일 명령 모드
"""

from __future__ import annotations

import shlex
import sys
from pathlib import Path

# F5에서 "현재 파일 실행"을 선택하면 cli.py가 패키지가 아닌 일반 파일로
# 실행된다. 그 경우 상대 import(.store)가 실패하므로, 부모 폴더를
# import 경로에 넣고 패키지 이름을 지정해 직접 실행도 가능하게 한다.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "mini_redis"

from .store import MiniRedis


ERR_INTEGER = "(error) ERR value is not an integer or out of range"


def run_command(store: MiniRedis, line: str) -> list[str] | None:
    """한 줄 명령을 실행하고 출력할 문자열 목록을 반환한다.

    반환 규칙:
    - list[str]: 화면에 한 줄씩 출력할 결과
    - []: 빈 입력이라 출력할 내용 없음
    - None: exit/quit 요청이라 프로그램 종료

    shlex.split()을 쓰기 때문에 SET name "Alice Kim"처럼 큰따옴표로
    감싼 값을 하나의 인자로 처리할 수 있다.
    """

    try:
        parts = shlex.split(line)
    except ValueError as exc:
        return [f"(error) ERR {exc}"]

    if not parts:
        return []

    command = parts[0].upper()
    if command in ("EXIT", "QUIT"):
        return None

    # 아래 분기들은 Redis 명령어 이름과 인자 개수를 먼저 확인한 뒤
    # 실제 처리는 store.py의 MiniRedis 메서드에 맡긴다.
    if command == "SET":
        if len(parts) != 3:
            return [_wrong_args(command)]
        return [store.set(parts[1], parts[2])]

    if command == "GET":
        if len(parts) != 2:
            return [_wrong_args(command)]
        return [store.get(parts[1])]

    if command == "DEL":
        if len(parts) != 2:
            return [_wrong_args(command)]
        return [store.delete(parts[1])]

    if command == "EXISTS":
        if len(parts) != 2:
            return [_wrong_args(command)]
        return [store.exists(parts[1])]

    if command == "DBSIZE":
        if len(parts) != 1:
            return [_wrong_args(command)]
        return [store.dbsize()]

    if command == "KEYS":
        if len(parts) != 1:
            return [_wrong_args(command)]
        keys = store.keys()
        if not keys:
            return ["(empty array)"]
        # Redis 배열 출력을 단순화해 과제 예시처럼 번호가 있는 줄로 출력한다.
        return [f'{index + 1}. "{key}"' for index, key in enumerate(keys)]

    if command == "EXPIRE":
        if len(parts) != 3:
            return [_wrong_args(command)]
        seconds = _parse_int(parts[2])
        if seconds is None:
            return [ERR_INTEGER]
        return [store.expire(parts[1], seconds)]

    if command == "TTL":
        if len(parts) != 2:
            return [_wrong_args(command)]
        return [store.ttl(parts[1])]

    if command == "CONFIG":
        return _run_config(store, parts)

    if command == "INFO":
        return _run_info(store, parts)

    return [f"(error) ERR unknown command '{parts[0]}'"]


def repl() -> int:
    """대화형 REPL을 실행한다.

    프로그램이 켜져 있는 동안 하나의 MiniRedis 인스턴스를 계속 사용하므로
    SET으로 저장한 값이 다음 GET에서도 유지된다.
    """
    store = MiniRedis()

    while True:
        try:
            line = input("mini-redis> ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 0

        output = run_command(store, line)
        if output is None:
            return 0
        for row in output:
            print(row)


def main(argv: list[str] | None = None) -> int:
    """CLI 진입점.

    argv가 비어 있으면 REPL 모드로 들어가고, argv가 있으면 해당 인자를
    하나의 명령처럼 처리한다. 단일 명령 모드는 간단한 동작 확인용이다.
    """
    args = sys.argv[1:] if argv is None else argv
    store = MiniRedis()

    if args:
        output = run_command(store, " ".join(args))
        if output is None:
            return 0
        for row in output:
            print(row)
        return 0

    return repl()


def _run_config(store: MiniRedis, parts: list[str]) -> list[str]:
    """CONFIG SET maxmemory 명령을 처리한다."""
    if len(parts) != 4:
        return [_wrong_args("CONFIG")]
    if parts[1].upper() != "SET" or parts[2].lower() != "maxmemory":
        return [f"(error) ERR unknown command '{' '.join(parts)}'"]

    maxmemory = _parse_int(parts[3])
    if maxmemory is None or maxmemory < 0:
        return [ERR_INTEGER]
    return [store.set_maxmemory(maxmemory)]


def _run_info(store: MiniRedis, parts: list[str]) -> list[str]:
    """INFO memory 명령을 처리한다."""
    if len(parts) != 2:
        return [_wrong_args("INFO")]
    if parts[1].lower() != "memory":
        return [f"(error) ERR unknown command '{' '.join(parts)}'"]
    return store.info_memory()


def _parse_int(raw: str) -> int | None:
    """문자열을 정수로 바꾼다. 실패하면 None을 반환한다."""
    try:
        return int(raw)
    except ValueError:
        return None


def _wrong_args(command: str) -> str:
    """Redis 스타일 인자 개수 오류 메시지를 만든다."""
    return f"(error) ERR wrong number of arguments for '{command}' command"


if __name__ == "__main__":
    sys.exit(main())

