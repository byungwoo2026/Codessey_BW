"""데코레이터 계층 — 공통 관심사(cross-cutting concern) 분리.

세 가지 공통 기능을 데코레이터로 분리해 비즈니스 로직과 섞이지 않게 한다.

* log_call     : 함수 호출/종료를 로그 파일에 기록
* timed        : 실행 시간(ms)을 측정해 로그에 기록
* handle_errors: AppError 를 잡아 스택트레이스 대신 '원인 + 힌트'로 출력하고
                 0이 아닌 종료 코드로 종료

로그는 stdout 을 더럽히지 않도록 파일(logging)로만 남긴다.
"""

from __future__ import annotations

import functools
import logging
import sys
import time
from typing import Callable, TypeVar

from .errors import AppError

F = TypeVar("F", bound=Callable[..., object])

logger = logging.getLogger("budget_app")


def log_call(func: F) -> F:
    """함수 호출 시작/종료를 로그로 남긴다."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug("call %s()", func.__qualname__)
        result = func(*args, **kwargs)
        logger.debug("done %s()", func.__qualname__)
        return result

    return wrapper  # type: ignore[return-value]


def timed(func: F) -> F:
    """실행 시간을 측정해 로그에 기록한다."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.debug("time %s() %.2fms", func.__qualname__, elapsed_ms)

    return wrapper  # type: ignore[return-value]


def handle_errors(func: Callable[..., int]) -> Callable[..., int]:
    """최상위 실행 함수를 감싸 예외를 사용자 친화적으로 처리한다.

    - AppError  : 원인 + 해결 힌트를 stderr 로 출력, 종료 코드 1
    - 기타 예외 : 짧은 원인만 출력(스택트레이스 숨김), 종료 코드 2
    - 정상      : 함수가 돌려준 종료 코드(기본 0)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> int:
        try:
            return func(*args, **kwargs)
        except AppError as exc:
            print(f"오류: {exc.message}", file=sys.stderr)
            if exc.hint:
                print(f"힌트: {exc.hint}", file=sys.stderr)
            logger.warning("AppError: %s", exc.message)
            return 1
        except KeyboardInterrupt:
            print("\n중단되었습니다.", file=sys.stderr)
            return 130
        except Exception as exc:  # noqa: BLE001 - 최상위 방어선
            print(f"오류: 예상치 못한 문제가 발생했습니다 ({exc})", file=sys.stderr)
            print("힌트: 입력값을 확인하거나 data 폴더의 파일 형식을 점검하세요.",
                  file=sys.stderr)
            logger.exception("unexpected error")
            return 2

    return wrapper
