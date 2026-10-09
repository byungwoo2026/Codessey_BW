"""
run_all.py : "도서 대여" DB 를 처음부터 만들고, SQL 파일 3개를 순서대로 실행해서
             쿼리 15개의 실행 결과를 텍스트 파일로 저장하는 스크립트.

사용법 (이 파일이 있는 폴더에서)
    python run_all.py

하는 일
    1. library.db 를 지우고 새로 만든다                    (매번 같은 결과가 나오게 하려고)
    2. sql/01_schema.sql      실행  → 테이블 4개 생성
    3. sql/02_insert_data.sql 실행  → 샘플 데이터 입력
       └ results/00_verify.txt 에 "행 수 / FK / 제약조건이 실제로 동작하는지" 검증 결과를 저장
    4. sql/03_queries.sql     실행  → results/Q01.txt ~ Q15.txt 에 쿼리와 결과를 저장
    5. results/all_results.txt (전체 모음), results/results.json (설명자료 생성용) 저장

※ 외부 라이브러리 없이 파이썬 기본 기능(sqlite3)만 사용한다.
"""

import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent
SQL_DIR = BASE / "sql"
RESULT_DIR = BASE / "results"
DB_PATH = BASE / "library.db"

# 쿼리 파일에서 "-- Q1. [기본 조회] 설명" 형태의 줄을 찾는 패턴
QUERY_MARK = re.compile(r"^--\s*(Q\d+)\.\s*(?:\[([^\]]+)\])?\s*(.*)$")


# ----------------------------------------------------------------------------
# 1. 표 모양 텍스트 만들기 (한글은 화면에서 2칸을 차지하므로 폭을 따로 계산)
# ----------------------------------------------------------------------------
def display_width(text: str) -> int:
    """문자열이 화면에서 차지하는 칸 수 (한글·전각 문자는 2칸)"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def pad(text: str, width: int, align_right: bool = False) -> str:
    gap = width - display_width(text)
    return (" " * gap + text) if align_right else (text + " " * gap)


def format_table(columns, rows) -> str:
    """컬럼명과 행 목록을 +---+ 모양의 표 문자열로 바꾼다."""
    cells = [["NULL" if v is None else str(v) for v in row] for row in rows]
    # 숫자만 들어 있는 컬럼은 오른쪽 정렬
    numeric = [
        bool(rows) and all(isinstance(r[i], (int, float)) or r[i] is None for r in rows)
        for i in range(len(columns))
    ]
    widths = [
        max([display_width(columns[i])] + [display_width(c[i]) for c in cells])
        for i in range(len(columns))
    ]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    out = [line]
    out.append("| " + " | ".join(pad(columns[i], widths[i]) for i in range(len(columns))) + " |")
    out.append(line)
    for c in cells:
        out.append("| " + " | ".join(pad(c[i], widths[i], numeric[i]) for i in range(len(columns))) + " |")
    out.append(line)
    return "\n".join(out)


# ----------------------------------------------------------------------------
# 2. SQL 파일을 "문장 단위"로 쪼개기
# ----------------------------------------------------------------------------
def has_code(lines) -> bool:
    return any(l.strip() and not l.strip().startswith("--") for l in lines)


def parse_script(text: str):
    """(쿼리정보 또는 None, SQL문장) 을 차례로 돌려준다.
    - '-- Q번호.' 줄을 만나면 새 쿼리 묶음이 시작된다.
    - 세미콜론으로 끝나는 완전한 문장이 되면 하나로 내보낸다. (sqlite3.complete_statement 사용)
    """
    current = None
    buf = []
    for line in text.splitlines():
        mark = QUERY_MARK.match(line)
        if mark and not has_code(buf):
            current = {"id": mark.group(1), "tag": mark.group(2) or "", "title": mark.group(3).strip()}
            buf = []  # 구역 제목 같은 주석은 버린다
            continue
        buf.append(line)
        sql = "\n".join(buf)
        if has_code(buf) and sqlite3.complete_statement(sql):
            yield current, sql.strip()
            buf = []
    if has_code(buf):
        raise ValueError("세미콜론(;) 없이 끝난 SQL 문장이 있습니다:\n" + "\n".join(buf))


def strip_comments(sql: str) -> str:
    return "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--")).strip()


# ----------------------------------------------------------------------------
# 3. SQL 한 문장을 실행하고 결과를 dict 로 정리
# ----------------------------------------------------------------------------
def run_statement(conn: sqlite3.Connection, sql: str) -> dict:
    cur = conn.execute(sql)
    result = {"sql": sql, "columns": [], "rows": [], "rowcount": None}
    if cur.description is not None:  # SELECT, EXPLAIN 처럼 표가 나오는 문장
        result["columns"] = [d[0] for d in cur.description]
        result["rows"] = [list(r) for r in cur.fetchall()]
        # EXPLAIN QUERY PLAN 은 마지막 'detail' 컬럼만 보여 주는 게 읽기 쉽다
        if strip_comments(sql).upper().startswith("EXPLAIN QUERY PLAN"):
            result["columns"] = ["plan"]
            result["rows"] = [[r[-1]] for r in result["rows"]]
    else:  # INSERT / UPDATE / DELETE / CREATE ...
        result["rowcount"] = cur.rowcount
    return result


def render_statement(result: dict, index: int, total: int) -> str:
    head = f"[SQL {index}/{total}]" if total > 1 else "[SQL]"
    lines = [head, result["sql"], ""]
    if result["columns"]:
        lines.append("[실행 결과]")
        lines.append(format_table(result["columns"], result["rows"]))
        lines.append(f"({len(result['rows'])}행)")
    elif result["rowcount"] is not None and result["rowcount"] >= 0:
        lines.append(f"[실행 결과] {result['rowcount']}행이 변경되었습니다.")
    else:
        lines.append("[실행 결과] 실행 완료 (출력 없음)")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# 4. 검증 : 행 수 / FK 목록 / 제약조건이 정말 동작하는지
# ----------------------------------------------------------------------------
TABLES = ["category", "member", "book", "rental"]


def count_rows(conn):
    return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLES}


def fk_list(conn):
    rows = []
    for t in TABLES:
        for r in conn.execute(f"PRAGMA foreign_key_list({t})"):
            # r = (id, seq, 참조테이블, 내 컬럼, 참조 컬럼, on_update, on_delete, match)
            rows.append([t, r[3], r[2], r[4], r[6]])
    return rows


def try_statement(conn, sql):
    """트랜잭션 안에서 실행해 보고 무조건 되돌린다. (검증 때문에 데이터가 바뀌면 안 되므로)"""
    conn.execute("BEGIN")
    try:
        conn.execute(sql)
        return "성공 (!)"
    except sqlite3.Error as e:
        return f"거부됨 → {type(e).__name__}: {e}"
    finally:
        conn.execute("ROLLBACK")


CONSTRAINT_TESTS = [
    ("FK : 존재하지 않는 회원(999번)으로 대여 기록 입력",
     "INSERT INTO rental (member_id, book_id, rented_at, due_date) VALUES (999, 1, '2026-10-08', '2026-10-22')"),
    ("FK : 존재하지 않는 도서(999번)로 대여 기록 입력",
     "INSERT INTO rental (member_id, book_id, rented_at, due_date) VALUES (1, 999, '2026-10-08', '2026-10-22')"),
    ("FK : 존재하지 않는 분류(99번)로 도서 입력",
     "INSERT INTO book (category_id, title, author, price) VALUES (99, '유령 책', '아무개', 10000)"),
    ("FK(RESTRICT) : 대여 기록이 남아 있는 도서(1번) 삭제",
     "DELETE FROM book WHERE book_id = 1"),
    ("FK(RESTRICT) : 대여 기록이 남아 있는 회원(1번) 삭제",
     "DELETE FROM member WHERE member_id = 1"),
    ("NOT NULL : 이름 없이 회원 입력",
     "INSERT INTO member (name, email, joined_at) VALUES (NULL, 'null.name@example.com', '2026-10-08')"),
    ("UNIQUE : 이미 있는 이메일로 회원 입력",
     "INSERT INTO member (name, email, joined_at) VALUES ('중복', 'minjun.kim@example.com', '2026-10-08')"),
    ("UNIQUE : 이미 있는 분류 이름 입력",
     "INSERT INTO category (name) VALUES ('소설')"),
    ("CHECK : 음수 가격으로 도서 입력",
     "INSERT INTO book (category_id, title, author, price) VALUES (1, '음수 책', '아무개', -1)"),
    ("CHECK : 허용되지 않은 상태값('LOST')으로 대여 기록 입력",
     "INSERT INTO rental (member_id, book_id, rented_at, due_date, status) VALUES (1, 1, '2026-10-08', '2026-10-22', 'LOST')"),
]


def build_verify(conn, label: str, with_tests: bool) -> dict:
    data = {
        "label": label,
        "foreign_keys_pragma": conn.execute("PRAGMA foreign_keys").fetchone()[0],
        "row_counts": count_rows(conn),
        "fk_list": fk_list(conn),
        "fk_check_violations": [list(r) for r in conn.execute("PRAGMA foreign_key_check")],
        "indexes": [[r[1], r[2]] for r in conn.execute("PRAGMA index_list(rental)")],
        "tests": [],
        "pragma_off_experiment": None,
    }
    if with_tests:
        for title, sql in CONSTRAINT_TESTS:
            data["tests"].append({"title": title, "sql": sql, "result": try_statement(conn, sql)})

        # 대조 실험 : PRAGMA foreign_keys 를 끄면 같은 잘못된 입력이 그냥 들어가 버린다
        bad = CONSTRAINT_TESTS[0][1]
        conn.execute("PRAGMA foreign_keys = OFF")
        outcome = try_statement(conn, bad)
        conn.execute("PRAGMA foreign_keys = ON")
        data["pragma_off_experiment"] = {"sql": bad, "result": outcome}
    return data


def render_verify(v: dict) -> str:
    out = [f"■ {v['label']}", "=" * 70, ""]
    out.append(f"PRAGMA foreign_keys 값 : {v['foreign_keys_pragma']}   (1 = FK 검사 켜짐)")
    out.append("")
    out.append("[테이블별 행 수]  요구사항 : 각 테이블 10행 이상")
    rows = [[t, n, "OK" if n >= 10 else "부족"] for t, n in v["row_counts"].items()]
    out.append(format_table(["table", "rows", "10행 이상?"], rows))
    out.append("")
    out.append("[외래키(FK) 목록]  자식 테이블.컬럼 → 부모 테이블.컬럼")
    out.append(format_table(["child_table", "child_column", "parent_table", "parent_column", "on_delete"], v["fk_list"]))
    out.append("")
    n = len(v["fk_check_violations"])
    out.append(f"[PRAGMA foreign_key_check] FK 를 어기고 있는 행 : {n}건" + ("  → 데이터 정합성 OK" if n == 0 else "  → 문제 있음!"))
    out.append("")
    out.append("[rental 테이블의 인덱스 목록]")
    out.append(format_table(["index_name", "unique(1/0)"], v["indexes"]) if v["indexes"] else "(없음 : 아직 CREATE INDEX 를 실행하기 전)")
    if v["tests"]:
        out.append("")
        out.append("[제약조건이 실제로 동작하는지 확인]  잘못된 입력을 일부러 시도 → 모두 거부되어야 한다 (시도 후 자동 롤백)")
        for i, t in enumerate(v["tests"], 1):
            out += ["", f"({i}) {t['title']}", f"    SQL   : {t['sql']}", f"    결과  : {t['result']}"]
        exp = v["pragma_off_experiment"]
        out += [
            "",
            "[참고 · 대조 실험] PRAGMA foreign_keys = OFF 로 끄면 어떻게 될까?  (SQLite 는 이걸 켜야 FK 가 동작한다)",
            f"    SQL   : {exp['sql']}",
            f"    결과  : {exp['result']}   ← 검사를 껐더니 없는 회원 번호가 그냥 들어간다 (시도 후 롤백)",
        ]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------
# 5. 메인
# ----------------------------------------------------------------------------
def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    RESULT_DIR.mkdir(exist_ok=True)
    for old in RESULT_DIR.glob("*"):
        if old.is_file():
            old.unlink()
    for leftover in (DB_PATH, DB_PATH.with_name(DB_PATH.name + "-journal")):
        if leftover.exists():
            leftover.unlink()

    # isolation_level=None : 파이썬이 몰래 트랜잭션을 열지 않게 하고, 문장마다 바로 반영
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")  # [SQLite 전용] 연결마다 켜야 한다

    # --- 01, 02 : 스키마 + 데이터 ---------------------------------------------------
    for name in ("01_schema.sql", "02_insert_data.sql"):
        text = (SQL_DIR / name).read_text(encoding="utf-8")
        n = 0
        for _, sql in parse_script(text):
            run_statement(conn, sql)
            n += 1
        print(f"[OK] {name} 실행 완료 ({n}개 문장)")

    verify_after_load = build_verify(conn, "데이터 입력 직후 (01, 02 실행 후 / 03 실행 전)", with_tests=True)

    # --- 03 : 쿼리 15개 ------------------------------------------------------------
    text = (SQL_DIR / "03_queries.sql").read_text(encoding="utf-8")
    blocks = {}  # Q번호 → {id, tag, title, statements}
    for info, sql in parse_script(text):
        result = run_statement(conn, sql)
        if info is None:  # 맨 위 PRAGMA 같은 준비용 문장
            continue
        block = blocks.setdefault(info["id"], {**info, "statements": []})
        block["statements"].append(result)

    verify_after_queries = build_verify(conn, "쿼리 실행 후 (03 까지 모두 실행한 최종 상태)", with_tests=False)
    conn.close()

    # --- 결과 저장 -------------------------------------------------------------------
    verify_text = render_verify(verify_after_load) + "\n\n" + render_verify(verify_after_queries)
    (RESULT_DIR / "00_verify.txt").write_text(verify_text, encoding="utf-8")

    all_parts = ["# 쿼리 15개 실행 결과 모음\n(python run_all.py 로 자동 생성 · DB: SQLite · 기준일 2026-10-08)\n"]
    for qid, block in blocks.items():
        number = int(qid[1:])
        head = "=" * 78 + f"\n{qid}. [{block['tag']}] {block['title']}\n" + "=" * 78
        body = "\n\n".join(
            render_statement(r, i, len(block["statements"])) for i, r in enumerate(block["statements"], 1)
        )
        text_out = head + "\n\n" + body + "\n"
        (RESULT_DIR / f"Q{number:02d}.txt").write_text(text_out, encoding="utf-8")
        all_parts.append(text_out)
    (RESULT_DIR / "all_results.txt").write_text("\n".join(all_parts), encoding="utf-8")

    payload = {
        "verify_after_load": verify_after_load,
        "verify_after_queries": verify_after_queries,
        "queries": list(blocks.values()),
    }
    (RESULT_DIR / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- 콘솔 요약 -------------------------------------------------------------------
    print(f"[OK] 03_queries.sql 실행 완료 (쿼리 {len(blocks)}개)")
    print()
    for qid, block in blocks.items():
        last = block["statements"][-1]
        shown = f"{len(last['rows'])}행 조회" if last["columns"] else f"{last['rowcount']}행 변경" if last["rowcount"] not in (None, -1) else "실행 완료"
        print(f"  {qid:<4} [{block['tag']}] {shown}")
    print()
    print("행 수 :", verify_after_load["row_counts"])
    print(f"결과 저장 위치 : {RESULT_DIR}")
    print(f"DB 파일        : {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
