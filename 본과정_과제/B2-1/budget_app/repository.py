"""저장소 계층 — 파일 I/O 담당.

저장 포맷: JSONL (한 줄에 JSON 객체 하나).
파일 3종:
    transactions.jsonl / categories.jsonl / budgets.jsonl

핵심 설계
--------
* 거래 조회는 파일을 통째로 메모리에 올리지 않고 '제너레이터로 스트리밍' 한다.
  - 최신순 조회는 파일을 뒤에서부터 블록 단위로 읽는 역방향 스트리밍으로 구현했다.
  - --limit N 이면 N개만 yield 하고 멈추므로 파일 전체를 읽지 않는다.
* update/delete 는 임시 파일에 다시 쓴 뒤 os.replace 로 '원자적 교체' 한다.
  (쓰다가 죽어도 원본이 깨지지 않는다.)
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Iterator, Optional

from .models import Budget, Category, Transaction


def _ensure_file(path: Path) -> None:
    """파일이 없으면 빈 파일로 생성한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()


def _read_lines_reverse(path: Path, chunk_size: int = 8192) -> Iterator[str]:
    """파일을 뒤에서부터 한 줄씩 스트리밍한다 (전체 로드 없음)."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        buffer = b""
        while pos > 0:
            read_size = min(chunk_size, pos)
            pos -= read_size
            f.seek(pos)
            chunk = f.read(read_size)
            buffer = chunk + buffer
            parts = buffer.split(b"\n")
            # 첫 조각은 아직 앞부분과 이어질 수 있으므로 buffer 로 보류
            buffer = parts[0]
            for raw in reversed(parts[1:]):
                line = raw.strip()
                if line:
                    yield line.decode("utf-8")
        tail = buffer.strip()
        if tail:
            yield tail.decode("utf-8")


class TransactionRepository:
    """거래 저장소 (스트리밍 조회 + 원자적 수정/삭제)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        _ensure_file(path)

    # ---- 쓰기 ----
    def append(self, tx: Transaction) -> None:
        """거래 한 건을 파일 끝에 추가한다."""
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(tx.to_dict(), ensure_ascii=False) + "\n")

    # ---- 스트리밍 읽기 ----
    def stream_newest_first(self) -> Iterator[Transaction]:
        """최신(마지막에 저장된) 거래부터 스트리밍한다."""
        for line in _read_lines_reverse(self.path):
            yield Transaction.from_dict(json.loads(line))

    def stream_oldest_first(self) -> Iterator[Transaction]:
        """오래된 거래부터 스트리밍한다 (파일을 앞에서부터 한 줄씩)."""
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield Transaction.from_dict(json.loads(line))

    # ---- 단건 조회 ----
    def get(self, tx_id: str) -> Optional[Transaction]:
        for tx in self.stream_newest_first():
            if tx.id == tx_id:
                return tx
        return None

    def count_by_category(self, category: str) -> int:
        return sum(1 for tx in self.stream_oldest_first() if tx.category == category)

    # ---- 원자적 재작성(수정/삭제/재분류) ----
    def _rewrite(self, transform) -> int:
        """전체를 스트리밍하며 transform 을 적용해 임시 파일에 다시 쓰고 교체한다.

        transform(tx) -> Transaction | None
            None 을 돌려주면 그 거래는 제외(삭제)된다.
        반환값: 실제로 바뀐(삭제/수정된) 건수.
        """
        changed = 0
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".tmp_", suffix=".jsonl"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as out:
                for tx in self.stream_oldest_first():
                    new_tx = transform(tx)
                    if new_tx is None:
                        changed += 1
                        continue
                    if new_tx is not tx:
                        changed += 1
                    out.write(json.dumps(new_tx.to_dict(), ensure_ascii=False) + "\n")
            os.replace(tmp_path, self.path)  # 원자적 교체
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
        return changed

    def update(self, tx_id: str, updated: Transaction) -> bool:
        """id 에 해당하는 거래를 updated 로 교체한다. 없으면 False."""
        found = False

        def transform(tx: Transaction):
            nonlocal found
            if tx.id == tx_id:
                found = True
                return updated
            return tx

        self._rewrite(transform)
        return found

    def delete(self, tx_id: str) -> bool:
        """id 에 해당하는 거래를 삭제한다. 없으면 False."""
        found = False

        def transform(tx: Transaction):
            nonlocal found
            if tx.id == tx_id:
                found = True
                return None
            return tx

        self._rewrite(transform)
        return found

    def reassign_category(self, old: str, new: str) -> int:
        """old 카테고리를 쓰는 모든 거래를 new 로 바꾼다. 바뀐 건수 반환."""

        def transform(tx: Transaction):
            if tx.category == old:
                return Transaction(
                    id=tx.id, type=tx.type, date=tx.date, amount=tx.amount,
                    category=new, memo=tx.memo, tags=tx.tags,
                )
            return tx

        return self._rewrite(transform)


class CategoryStore:
    """카테고리 저장소 (작아서 전체 로드해도 무방)."""

    DEFAULTS = ("food", "transport", "rent", "salary", "etc")

    def __init__(self, path: Path) -> None:
        self.path = path
        _ensure_file(path)

    def all(self) -> list[Category]:
        result: list[Category] = []
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    result.append(Category.from_dict(json.loads(line)))
        return result

    def names(self) -> list[str]:
        return [c.name for c in self.all()]

    def exists(self, name: str) -> bool:
        return name in set(self.names())

    def _write_all(self, categories: list[Category]) -> None:
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".tmp_", suffix=".jsonl"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            for c in categories:
                out.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")
        os.replace(tmp_path, self.path)

    def add(self, name: str) -> bool:
        """이미 있으면 False, 추가하면 True."""
        if self.exists(name):
            return False
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(Category(name).to_dict(), ensure_ascii=False) + "\n")
        return True

    def remove(self, name: str) -> bool:
        """있으면 삭제 후 True, 없으면 False."""
        current = self.all()
        remaining = [c for c in current if c.name != name]
        if len(remaining) == len(current):
            return False
        self._write_all(remaining)
        return True

    def ensure_defaults(self) -> None:
        """카테고리가 비어 있으면 기본 카테고리를 자동 생성한다 (안 A)."""
        if not self.names():
            self._write_all([Category(n) for n in self.DEFAULTS])


class BudgetStore:
    """월 예산 저장소 (month -> amount upsert)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        _ensure_file(path)

    def all(self) -> dict[str, int]:
        result: dict[str, int] = {}
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    b = Budget.from_dict(json.loads(line))
                    result[b.month] = b.amount
        return result

    def get(self, month: str) -> Optional[int]:
        return self.all().get(month)

    def set(self, month: str, amount: int) -> None:
        """해당 월 예산을 upsert 한다."""
        data = self.all()
        data[month] = amount
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".tmp_", suffix=".jsonl"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            for m in sorted(data):
                out.write(
                    json.dumps(Budget(m, data[m]).to_dict(), ensure_ascii=False) + "\n"
                )
        os.replace(tmp_path, self.path)
