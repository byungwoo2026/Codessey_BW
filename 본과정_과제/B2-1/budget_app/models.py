"""데이터 모델 계층.

가계부의 핵심 데이터 구조를 dataclass 로 정의합니다.
타입 힌트로 각 필드의 계약(contract)을 명확히 하고,
JSONL 저장/복원을 위한 직렬화 메서드를 함께 제공합니다.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

# 허용되는 거래 타입
INCOME = "income"
EXPENSE = "expense"
VALID_TYPES = (INCOME, EXPENSE)


def new_id() -> str:
    """짧고 유일한 거래 id 를 생성한다."""
    return uuid.uuid4().hex[:10]


@dataclass
class Transaction:
    """거래 한 건.

    필드
    ----
    id       : 유일 식별자
    type     : 'income' | 'expense'
    date     : YYYY-MM-DD
    amount   : 양의 정수
    category : 등록된 카테고리 이름
    memo     : 자유 메모 (선택)
    tags     : 태그 목록 (선택)
    """

    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def month(self) -> str:
        """YYYY-MM 형태의 월 문자열."""
        return self.date[:7]

    def to_dict(self) -> dict:
        """JSONL 저장용 dict 로 변환."""
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "memo": self.memo,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Transaction":
        """저장된 dict 로부터 Transaction 복원."""
        return cls(
            id=str(raw["id"]),
            type=str(raw["type"]),
            date=str(raw["date"]),
            amount=int(raw["amount"]),
            category=str(raw["category"]),
            memo=str(raw.get("memo", "")),
            tags=list(raw.get("tags", [])),
        )


@dataclass
class Category:
    """카테고리."""

    name: str

    def to_dict(self) -> dict:
        return {"name": self.name}

    @classmethod
    def from_dict(cls, raw: dict) -> "Category":
        return cls(name=str(raw["name"]))


@dataclass
class Budget:
    """월 예산."""

    month: str  # YYYY-MM
    amount: int

    def to_dict(self) -> dict:
        return {"month": self.month, "amount": self.amount}

    @classmethod
    def from_dict(cls, raw: dict) -> "Budget":
        return cls(month=str(raw["month"]), amount=int(raw["amount"]))


# ---- 검증 유틸 (모델 계약을 지키기 위한 헬퍼) ----

def parse_date(value: str) -> str:
    """YYYY-MM-DD 형식을 검증하고 정규화한 문자열을 돌려준다."""
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(str(exc)) from exc


def parse_month(value: str) -> str:
    """YYYY-MM 형식을 검증하고 정규화한 문자열을 돌려준다."""
    try:
        return datetime.strptime(value.strip(), "%Y-%m").strftime("%Y-%m")
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
