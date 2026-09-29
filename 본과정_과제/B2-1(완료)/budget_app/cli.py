"""CLI 계층 — 명령 파싱, 대화형 입력, 출력 포맷.

실행:  python -m budget_app <command> [options]
모든 명령은 --help 로 사용법을 볼 수 있다 (argparse 기본 제공).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .decorators import handle_errors
from .errors import ValidationError
from .models import VALID_TYPES
from .repository import BudgetStore, CategoryStore, TransactionRepository
from .service import BudgetService, MonthlySummary, SearchFilter

DEFAULT_DATA_DIR = "./data"


# ============ 조립 ============

def _build_service(data_dir: Path) -> BudgetService:
    data_dir.mkdir(parents=True, exist_ok=True)
    tx_repo = TransactionRepository(data_dir / "transactions.jsonl")
    cat_store = CategoryStore(data_dir / "categories.jsonl")
    budget_store = BudgetStore(data_dir / "budgets.jsonl")
    cat_store.ensure_defaults()  # 비어 있으면 기본 카테고리 자동 생성 (안 A)
    return BudgetService(tx_repo, cat_store, budget_store)


def _setup_logging(data_dir: Path) -> None:
    logging.basicConfig(
        filename=str(data_dir / "app.log"),
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
    )


# ============ 대화형 입력 헬퍼 ============

def _prompt(label: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default


def _prompt_choice(label: str, choices: tuple[str, ...]) -> str:
    while True:
        value = _prompt(f"{label} ({'/'.join(choices)})")
        if value in choices:
            return value
        print(f"  → {choices} 중에서 입력하세요.")


def _prompt_amount(label: str) -> int:
    while True:
        raw = _prompt(label)
        try:
            amount = int(raw)
        except ValueError:
            print("  → 정수를 입력하세요.")
            continue
        if amount <= 0:
            print("  → 0보다 큰 금액을 입력하세요.")
            continue
        return amount


def _prompt_date(label: str) -> str:
    from .models import parse_date
    while True:
        raw = _prompt(label)
        try:
            return parse_date(raw)
        except ValueError:
            print("  → YYYY-MM-DD 형식으로 입력하세요. 예: 2026-07-08")


def _prompt_category(label: str, service: BudgetService) -> str:
    names = service.list_categories()
    print(f"  등록된 카테고리: {', '.join(names) or '(없음)'}")
    while True:
        raw = _prompt(label)
        if raw in names:
            return raw
        print(f"  → 등록된 카테고리가 아닙니다. category add 로 먼저 등록하거나 목록에서 고르세요.")


# ============ 출력 헬퍼 ============

def _print_tx_line(tx) -> None:
    sign = "+" if tx.type == "income" else "-"
    tags = f" #{' #'.join(tx.tags)}" if tx.tags else ""
    memo = f"  {tx.memo}" if tx.memo else ""
    print(
        f"{tx.date}  {tx.id}  {sign}{tx.amount:>10,}  "
        f"[{tx.category}]{memo}{tags}"
    )


def _print_summary(s: MonthlySummary) -> None:
    print(f"== {s.month} 요약 ==")
    if not s.has_data:
        print("데이터 없음")
        return
    print(f"총 수입 : {s.total_income:>12,}")
    print(f"총 지출 : {s.total_expense:>12,}")
    print(f"잔  액 : {s.balance:>12,}")
    if s.budget is not None:
        print(f"예  산 : {s.budget:>12,}  (사용률 {s.budget_used_pct}%)")
        if s.over_budget:
            over = s.total_expense - s.budget
            print(f"⚠️  예산 초과! {over:,} 만큼 초과했습니다.")
    if s.top_categories:
        print(f"-- 카테고리별 지출 TOP {len(s.top_categories)} --")
        for name, total in s.top_categories:
            print(f"  {name:<12} {total:>12,}")


# ============ 명령 핸들러 ============

def cmd_add(args: argparse.Namespace, service: BudgetService) -> int:
    print("새 거래를 입력합니다. (빈 값이면 기본값/건너뛰기)")
    date = _prompt_date("날짜(YYYY-MM-DD)")
    type_ = _prompt_choice("타입", VALID_TYPES)
    category = _prompt_category("카테고리", service)
    amount = _prompt_amount("금액")
    memo = input("메모(선택): ").strip()
    tags_raw = input("태그(쉼표 구분, 선택): ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    tx = service.add_transaction(
        type=type_, date=date, amount=amount,
        category=category, memo=memo, tags=tags,
    )
    print(f"저장 완료. id = {tx.id}")
    return 0


def cmd_list(args: argparse.Namespace, service: BudgetService) -> int:
    printed = 0
    for tx in service.list_transactions(limit=args.limit):
        _print_tx_line(tx)
        printed += 1
    if printed == 0:
        print("거래가 없습니다. add 로 추가해 보세요.")
    else:
        print(f"-- 총 {printed}건 (최신순, limit={args.limit}) --")
    return 0


def cmd_search(args: argparse.Namespace, service: BudgetService) -> int:
    flt = SearchFilter(
        date_from=args.date_from, date_to=args.date_to,
        category=args.category, type=args.type,
        query=args.q, tag=args.tag,
    )
    printed = 0
    for tx in service.search_transactions(flt):
        _print_tx_line(tx)
        printed += 1
    print(f"-- 검색 결과 {printed}건 --")
    return 0


def cmd_summary(args: argparse.Namespace, service: BudgetService) -> int:
    s = service.summary(args.month, top=args.top)
    _print_summary(s)
    return 0


def cmd_budget(args: argparse.Namespace, service: BudgetService) -> int:
    if args.action == "set":
        if args.month is None or args.amount is None:
            raise ValidationError(
                "budget set 에는 --month 와 --amount 가 필요합니다.",
                "예: budget set --month 2026-07 --amount 1500000",
            )
        service.set_budget(args.month, args.amount)
        print(f"예산 저장 완료: {args.month} → {args.amount:,}")
    return 0


def cmd_category(args: argparse.Namespace, service: BudgetService) -> int:
    if args.action == "list":
        names = service.list_categories()
        print("카테고리 목록:")
        for n in names:
            print(f"  - {n}")
        if not names:
            print("  (없음)")
    elif args.action == "add":
        if not args.name:
            raise ValidationError("추가할 카테고리 이름이 필요합니다.",
                                  "예: category add grocery")
        service.add_category(args.name)
        print(f"카테고리 추가 완료: {args.name}")
    elif args.action == "remove":
        if not args.name:
            raise ValidationError("삭제할 카테고리 이름이 필요합니다.",
                                  "예: category remove grocery")
        reassigned = service.remove_category(args.name, replace=args.replace)
        if reassigned:
            print(f"'{args.name}' 사용 거래 {reassigned}건을 '{args.replace}'로 재분류 후 삭제했습니다.")
        else:
            print(f"카테고리 삭제 완료: {args.name}")
    return 0


def cmd_update(args: argparse.Namespace, service: BudgetService) -> int:
    fields = {}
    if args.date is not None:
        fields["date"] = args.date
    if args.type is not None:
        fields["type"] = args.type
    if args.category is not None:
        fields["category"] = args.category
    if args.amount is not None:
        fields["amount"] = args.amount
    if args.memo is not None:
        fields["memo"] = args.memo
    if args.tags is not None:
        fields["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not fields:
        raise ValidationError(
            "수정할 항목이 없습니다.",
            "--date/--type/--category/--amount/--memo/--tags 중 하나 이상 지정하세요.",
        )
    updated = service.update_transaction(args.id, **fields)
    print(f"수정 완료: {updated.id}")
    _print_tx_line(updated)
    return 0


def cmd_delete(args: argparse.Namespace, service: BudgetService) -> int:
    service.delete_transaction(args.id)
    print(f"삭제 완료: {args.id}")
    return 0


def cmd_import(args: argparse.Namespace, service: BudgetService) -> int:
    ok, failed = service.import_csv(Path(args.date_from_file))
    print(f"가져오기 완료: 성공 {ok}건, 실패 {failed}건")
    return 0


def cmd_export(args: argparse.Namespace, service: BudgetService) -> int:
    if not args.month and not (args.date_from and args.date_to):
        raise ValidationError(
            "export 에는 --month 또는 (--from 과 --to) 조건이 필요합니다.",
            "예: export --out out.csv --month 2026-07",
        )
    if args.month:
        from .models import parse_month
        try:
            m = parse_month(args.month)
        except ValueError:
            raise ValidationError(f"월 형식 오류: {args.month!r}", "YYYY-MM 형식으로.")
        flt = SearchFilter(date_from=f"{m}-01", date_to=f"{m}-31")
    else:
        flt = SearchFilter(date_from=args.date_from, date_to=args.date_to)
    count = service.export_csv(Path(args.out), flt)
    print(f"내보내기 완료: {count}건 → {args.out}")
    return 0


# ============ 파서 구성 ============

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="파일 기반 콘솔 가계부 (JSONL 저장 · 제너레이터 스트리밍)",
    )
    parser.add_argument(
        "--data-dir", default=DEFAULT_DATA_DIR,
        help=f"데이터 저장 폴더 (기본: {DEFAULT_DATA_DIR})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add (대화형)
    sub.add_parser("add", help="거래 추가 (대화형 입력)")

    # list
    p_list = sub.add_parser("list", help="거래 목록 (최신순, 스트리밍)")
    p_list.add_argument("--limit", type=int, default=20, help="출력 개수 (기본 20)")

    # search
    p_search = sub.add_parser("search", help="거래 검색 (최신순, 스트리밍)")
    p_search.add_argument("--from", dest="date_from", help="시작일 YYYY-MM-DD")
    p_search.add_argument("--to", dest="date_to", help="종료일 YYYY-MM-DD")
    p_search.add_argument("--category", help="카테고리")
    p_search.add_argument("--type", choices=VALID_TYPES, help="income/expense")
    p_search.add_argument("--q", help="메모 키워드")
    p_search.add_argument("--tag", help="태그")

    # summary
    p_sum = sub.add_parser("summary", help="월별 요약")
    p_sum.add_argument("--month", required=True, help="YYYY-MM")
    p_sum.add_argument("--top", type=int, default=5, help="카테고리 TOP N (기본 5)")

    # budget set
    p_budget = sub.add_parser("budget", help="예산 설정")
    p_budget.add_argument("action", choices=["set"], help="set")
    p_budget.add_argument("--month", help="YYYY-MM")
    p_budget.add_argument("--amount", type=int, help="예산 금액")

    # category add/list/remove
    p_cat = sub.add_parser("category", help="카테고리 관리")
    p_cat.add_argument("action", choices=["add", "list", "remove"])
    p_cat.add_argument("name", nargs="?", help="카테고리 이름 (add/remove)")
    p_cat.add_argument("--replace", help="remove 시 사용 중이면 대체할 카테고리")

    # update (옵션 기반, 안 A)
    p_upd = sub.add_parser("update", help="거래 수정 (옵션 기반)")
    p_upd.add_argument("--id", required=True, help="수정할 거래 id")
    p_upd.add_argument("--date", help="YYYY-MM-DD")
    p_upd.add_argument("--type", choices=VALID_TYPES)
    p_upd.add_argument("--category")
    p_upd.add_argument("--amount", type=int)
    p_upd.add_argument("--memo")
    p_upd.add_argument("--tags", help="쉼표 구분 태그")

    # delete
    p_del = sub.add_parser("delete", help="거래 삭제")
    p_del.add_argument("--id", required=True, help="삭제할 거래 id")

    # import
    p_imp = sub.add_parser("import", help="CSV 가져오기")
    p_imp.add_argument("--from", dest="date_from_file", required=True,
                       help="가져올 CSV 경로")

    # export
    p_exp = sub.add_parser("export", help="CSV 내보내기")
    p_exp.add_argument("--out", required=True, help="저장할 CSV 경로")
    p_exp.add_argument("--month", help="YYYY-MM (또는 --from/--to)")
    p_exp.add_argument("--from", dest="date_from", help="시작일 YYYY-MM-DD")
    p_exp.add_argument("--to", dest="date_to", help="종료일 YYYY-MM-DD")

    return parser


_HANDLERS = {
    "add": cmd_add,
    "list": cmd_list,
    "search": cmd_search,
    "summary": cmd_summary,
    "budget": cmd_budget,
    "category": cmd_category,
    "update": cmd_update,
    "delete": cmd_delete,
    "import": cmd_import,
    "export": cmd_export,
}


@handle_errors
def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    _setup_logging(data_dir)
    service = _build_service(data_dir)

    handler = _HANDLERS[args.command]
    return handler(args, service)
