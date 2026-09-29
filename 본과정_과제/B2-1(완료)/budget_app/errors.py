"""애플리케이션 공통 예외 정의.

스택트레이스 대신 '원인 + 해결 힌트'를 사용자에게 보여주기 위한 예외 계층입니다.
"""

from __future__ import annotations


class AppError(Exception):
    """사용자에게 보여줄 원인(message)과 해결 힌트(hint)를 담는 예외."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


class ValidationError(AppError):
    """입력 검증 실패 (날짜 형식, 금액, 타입, 카테고리 등)."""


class NotFoundError(AppError):
    """존재하지 않는 데이터 (없는 id 등)."""


class ConflictError(AppError):
    """상태 충돌 (사용 중 카테고리 삭제 시도 등)."""
