"""서비스 계층 — 비즈니스 로직.

CLI 와 저장소 사이에서 검증/집계/조립을 담당한다.
공통 관심사(로그/시간측정) 데코레이터를 실제 메서드에 적용한다.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

from .decorators import log_call, timed
from .errors import ConflictError, NotFoundError, ValidationError
from .models import (
    VALID_TYPES,
    Transaction,
    new_id,
    parse_date,
    parse_month,
)
from .repository import BudgetStore, CategoryStore, TransactionRepository

CSV_COLUMNS = ["date", "type", "category", "amount", "memo", "tags"]


@dataclass
class SearchFilter:
    """search/export 공통 검색 조건."""

    date_from: Optional[str] = None
    date_to: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    query: Optional[str] = None  # 메모 키워드
    tag: Optional[str] = None

    def matches(self, tx: Transaction) -> bool:
        if self.date_from and tx.date < self.date_from:
            return False
        if self.date_to and tx.date > self.date_to:
            return False
        if self.category and tx.category != self.category:
            return False
        if self.type and tx.type != self.type:
            return False
        if self.query and self.query.lower() not in tx.memo.lower():
            return False
        if self.tag and self.tag not in tx.tags:
            return False
        return True


@dataclass
class MonthlySummary:
    """summary 결과 컨테이너."""

    month: str
    total_income: int
    total_expense: int
    balance: int
    top_categories: list[tuple[str, int]]
    has_data: bool
    budget: Optional[int] = None
    budget_used_pct: Optional[float] = None
    over_budget: bool = False


class BudgetService:
    """가계부 핵심 서비스."""

    def __init__(
        self,
        transactions: TransactionRepository,
        categories: CategoryStore,
        budgets: BudgetStore,
    ) -> None:
        self.transactions = transactions
        self.categories = categories
        self.budgets = budgets

    # ---------- 검증 헬퍼 ----------
    def _validate_type(self, type_: str) -> str:
        if type_ not in VALID_TYPES:
            raise ValidationError(
                f"허용되지 않은 타입입니다: {type_!r}",
                f"income 또는 expense 중 하나를 입력하세요.",
            )
        return type_

    def _validate_amount(self, amount: int) -> int:
        if amount <= 0:
            raise ValidationError(
                f"금액은 양수여야 합니다: {amount}",
                "0보다 큰 정수를 입력하세요.",
            )
        return amount

    def _validate_date(self, date: str) -> str:
        try:
            return parse_date(date)
        except ValueError:
            raise ValidationError(
                f"날짜 형식이 올바르지 않습니다: {date!r}",
                "YYYY-MM-DD 형식으로 입력하세요. 예: 2026-07-08",
            )

    def _validate_month(self, month: str) -> str:
        try:
            return parse_month(month)
        except ValueError:
            raise ValidationError(
                f"월 형식이 올바르지 않습니다: {month!r}",
                "YYYY-MM 형식으로 입력하세요. 예: 2026-07",
            )

    def _validate_category(self, category: str) -> str:
        if not self.categories.exists(category):
            raise ValidationError(
                f"등록되지 않은 카테고리입니다: {category!r}",
                "category list 로 확인하거나 category add 로 먼저 등록하세요. "
                f"현재: {', '.join(self.categories.names()) or '(없음)'}",
            )
        return category

    # ---------- 거래 추가 ----------
    @log_call
    @timed
    def add_transaction(
        self,
        *,
        type: str,
        date: str,
        amount: int,
        category: str,
        memo: str = "",
        tags: Optional[list[str]] = None,
    ) -> Transaction:
        tx = Transaction(
            id=new_id(),
            type=self._validate_type(type),
            date=self._validate_date(date),
            amount=self._validate_amount(amount),
            category=self._validate_category(category),
            memo=memo.strip(),
            tags=[t.strip() for t in (tags or []) if t.strip()],
        )
        self.transactions.append(tx)
        return tx

    # ---------- 목록 (스트리밍, 최신순) ----------
    @log_call
    def list_transactions(self, limit: int = 20) -> Iterator[Transaction]:
        count = 0
        for tx in self.transactions.stream_newest_first():
            if count >= limit:
                break
            yield tx
            count += 1

    # ---------- 검색 (스트리밍, 최신순) ----------
    @log_call
    @timed
    def search_transactions(self, flt: SearchFilter) -> Iterator[Transaction]:
        if flt.date_from:
            flt.date_from = self._validate_date(flt.date_from)
        if flt.date_to:
            flt.date_to = self._validate_date(flt.date_to)
        if flt.type:
            self._validate_type(flt.type)
        for tx in self.transactions.stream_newest_first():
            if flt.matches(tx):
                yield tx

    # ---------- 월별 요약 ----------
    @log_call
    @timed
    def summary(self, month: str, top: int = 5) -> MonthlySummary:
        month = self._validate_month(month)
        total_income = 0
        total_expense = 0
        by_category: dict[str, int] = {}
        has_data = False

        for tx in self.transactions.stream_oldest_first():
            if tx.month != month:
                continue
            has_data = True
            if tx.type == "income":
                total_income += tx.amount
            else:
                total_expense += tx.amount
                by_category[tx.category] = by_category.get(tx.category, 0) + tx.amount

        top_categories = sorted(
            by_category.items(), key=lambda kv: kv[1], reverse=True
        )[:top]

        budget = self.budgets.get(month)
        used_pct: Optional[float] = None
        over = False
        if budget is not None and budget > 0:
            used_pct = round(total_expense / budget * 100, 1)
            over = total_expense > budget

        return MonthlySummary(
            month=month,
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            top_categories=top_categories,
            has_data=has_data,
            budget=budget,
            budget_used_pct=used_pct,
            over_budget=over,
        )

    # ---------- 예산 ----------
    @log_call
    def set_budget(self, month: str, amount: int) -> None:
        month = self._validate_month(month)
        self._validate_amount(amount)
        self.budgets.set(month, amount)

    # ---------- 카테고리 ----------
    @log_call
    def list_categories(self) -> list[str]:
        return self.categories.names()

    @log_call
    def add_category(self, name: str) -> None:
        name = name.strip()
        if not name:
            raise ValidationError("카테고리 이름이 비어 있습니다.", "이름을 입력하세요.")
        if not self.categories.add(name):
            raise ConflictError(
                f"이미 존재하는 카테고리입니다: {name!r}", "다른 이름을 사용하세요."
            )

    @log_call
    def remove_category(self, name: str, replace: Optional[str] = None) -> int:
        """카테고리 삭제.

        사용 중이면:
        - replace 가 주어지면 해당 카테고리로 재분류 후 삭제
        - 없으면 삭제를 막고 안내 (ConflictError)
        반환값: 재분류된 거래 건수 (없으면 0).
        """
        if not self.categories.exists(name):
            raise NotFoundError(
                f"없는 카테고리입니다: {name!r}", "category list 로 확인하세요."
            )
        in_use = self.transactions.count_by_category(name)
        reassigned = 0
        if in_use > 0:
            if replace is None:
                raise ConflictError(
                    f"'{name}' 카테고리를 쓰는 거래가 {in_use}건 있어 삭제할 수 없습니다.",
                    f"--replace <대체카테고리> 로 재분류 후 삭제하세요.",
                )
            if not self.categories.exists(replace):
                raise ValidationError(
                    f"대체 카테고리가 등록되어 있지 않습니다: {replace!r}",
                    "먼저 category add 로 등록하세요.",
                )
            if replace == name:
                raise ValidationError(
                    "대체 카테고리가 삭제 대상과 같습니다.", "다른 카테고리를 지정하세요."
                )
            reassigned = self.transactions.reassign_category(name, replace)
        self.categories.remove(name)
        return reassigned

    # ---------- 수정 (옵션 기반, 안 A) ----------
    @log_call
    @timed
    def update_transaction(self, tx_id: str, **fields) -> Transaction:
        current = self.transactions.get(tx_id)
        if current is None:
            raise NotFoundError(
                f"해당 id 의 거래가 없습니다: {tx_id!r}", "list 로 id 를 확인하세요."
            )
        new_type = fields.get("type", current.type)
        new_date = fields.get("date", current.date)
        new_amount = fields.get("amount", current.amount)
        new_category = fields.get("category", current.category)
        new_memo = fields.get("memo", current.memo)
        new_tags = fields.get("tags", current.tags)

        updated = Transaction(
            id=current.id,
            type=self._validate_type(new_type),
            date=self._validate_date(new_date),
            amount=self._validate_amount(int(new_amount)),
            category=self._validate_category(new_category),
            memo=(new_memo or "").strip(),
            tags=[t.strip() for t in new_tags if t.strip()],
        )
        self.transactions.update(tx_id, updated)
        return updated

    # ---------- 삭제 ----------
    @log_call
    def delete_transaction(self, tx_id: str) -> None:
        if not self.transactions.delete(tx_id):
            raise NotFoundError(
                f"해당 id 의 거래가 없습니다: {tx_id!r}", "list 로 id 를 확인하세요."
            )

    # ---------- 가져오기 ----------
    @log_call
    @timed
    def import_csv(self, path: Path) -> tuple[int, int]:
        """CSV 를 읽어 일괄 등록한다. (성공 건수, 실패 건수) 반환."""
        if not path.exists():
            raise NotFoundError(
                f"import 대상 파일이 없습니다: {path}", "경로를 확인하세요."
            )
        ok = 0
        failed = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing = [c for c in ("date", "type", "category", "amount")
                       if c not in (reader.fieldnames or [])]
            if missing:
                raise ValidationError(
                    f"CSV 필수 컬럼 누락: {', '.join(missing)}",
                    "date,type,category,amount 컬럼이 필요합니다.",
                )
            for row in reader:
                try:
                    tags_raw = (row.get("tags") or "").strip()
                    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
                    self.add_transaction(
                        type=(row["type"] or "").strip(),
                        date=(row["date"] or "").strip(),
                        amount=int((row["amount"] or "0").strip()),
                        category=(row["category"] or "").strip(),
                        memo=(row.get("memo") or "").strip(),
                        tags=tags,
                    )
                    ok += 1
                except (ValidationError, ValueError):
                    failed += 1
        return ok, failed

    # ---------- 내보내기 ----------
    @log_call
    @timed
    def export_csv(self, path: Path, flt: SearchFilter) -> int:
        """조건에 맞는 거래를 CSV 로 저장한다. 저장 건수 반환."""
        rows = list(self.search_transactions(flt))
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            for tx in rows:
                writer.writerow([
                    tx.date, tx.type, tx.category, tx.amount,
                    tx.memo, ",".join(tx.tags),
                ])
        return len(rows)
