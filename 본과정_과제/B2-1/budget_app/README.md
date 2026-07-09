# budget_app — 파일 기반 콘솔 가계부

수입/지출을 파일에 영구 저장하고 CRUD·검색·월별요약·예산·카테고리 관리·CSV 입출력을
지원하는 콘솔 가계부입니다. **제너레이터 스트리밍**, **데코레이터 분리**, **타입 힌트**,
**계층형 모듈 구조**를 적용해 "유지보수 가능한 작은 서비스"로 설계했습니다.

---

## 1. 실행 방법

Python 3.10+ 필요 (외부 패키지 없음, 표준 라이브러리만 사용).

```bash
# 프로젝트 루트(budget_app 폴더의 상위)에서 실행
python -m budget_app <command> [options]

# 모든 명령은 --help 지원
python -m budget_app --help
python -m budget_app summary --help
```

저장 폴더는 기본 `./data` 이며 `--data-dir` 로 변경할 수 있습니다.

```bash
python -m budget_app --data-dir ./mydata list
```

---

## 2. 저장 파일 위치 / 형식

기본 폴더 `./data/` 에 **JSONL**(한 줄에 JSON 객체 하나)로 저장됩니다.
저장 파일이 없으면 자동 생성되며, 카테고리가 비어 있으면 기본 카테고리
(`food, transport, rent, salary, etc`)를 자동 생성합니다. **(초기화 정책: 안 A)**

| 파일 | 내용 | 한 줄 예시 |
| --- | --- | --- |
| `data/transactions.jsonl` | 거래 내역 | `{"id":"1ce00e0944","type":"income","date":"2026-07-01","amount":3000000,"category":"salary","memo":"7월 급여","tags":["월급"]}` |
| `data/categories.jsonl` | 카테고리 | `{"name":"food"}` |
| `data/budgets.jsonl` | 월 예산 | `{"month":"2026-07","amount":500000}` |
| `data/app.log` | 실행 로그(데코레이터가 기록) | — |

---

## 3. 주요 명령 예시

```bash
# 거래 추가 (대화형: 날짜/타입/카테고리/금액/메모/태그를 순서대로 입력)
python -m budget_app add

# 목록 (최신순, 스트리밍) — 기본 20건, --limit 로 조절
python -m budget_app list --limit 10

# 검색 (기간/카테고리/타입/메모키워드/태그)
python -m budget_app search --from 2026-07-01 --to 2026-07-31 --category food
python -m budget_app search --type expense --q 마트 --tag 생필품

# 월별 요약 (총수입/총지출/잔액 + 카테고리 지출 TOP N)
python -m budget_app summary --month 2026-07 --top 3

# 예산 설정 → summary 실행 시 사용률(%)/초과 경고 표시
python -m budget_app budget set --month 2026-07 --amount 500000

# 카테고리 관리
python -m budget_app category list
python -m budget_app category add grocery
python -m budget_app category remove food                 # 사용 중이면 삭제 차단
python -m budget_app category remove food --replace etc   # 재분류 후 삭제

# 수정 (옵션 기반 — 아래 4번 참고) / 삭제
python -m budget_app update --id 60544191bf --amount 18000 --memo "점심 수정"
python -m budget_app delete --id 14bf71a090

# CSV 가져오기 / 내보내기
python -m budget_app import --from transactions_in.csv
python -m budget_app export --out out.csv --month 2026-07
python -m budget_app export --out out.csv --from 2026-07-01 --to 2026-07-31
```

---

## 4. update 입력 방식 (문서 고정)

`update` 는 **옵션 기반(안 A)** 으로 고정합니다.

```
update --id <id> [--date YYYY-MM-DD] [--type income|expense]
                 [--category <name>] [--amount <양의정수>]
                 [--memo <문자열>] [--tags "a,b,c"]
```

- 지정한 필드만 변경하고 나머지는 유지합니다.
- 없는 `--id` 는 오류 메시지 + 종료 코드 1 로 처리합니다.
- 파일 기반 저장에서 수정/삭제는 **임시 파일에 다시 쓴 뒤 `os.replace` 로 원자적 교체**하여,
  쓰는 도중 중단돼도 원본이 깨지지 않습니다.

---

## 5. import / export CSV 스키마

공통: **UTF-8, 헤더 포함**.

| column | 필수 | 설명 |
| --- | --- | --- |
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 양의 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표(,) 구분 문자열 |

예시 (`transactions_in.csv`):

```csv
date,type,category,amount,memo,tags
2026-08-01,income,salary,3200000,8월 급여,월급
2026-08-02,expense,transport,120000,교통비,
2026-08-03,expense,food,9500,커피,카페
```

- `import`: 유효한 행만 등록하고 **성공/실패 건수**를 출력합니다
  (날짜 오류·음수 금액·미등록 카테고리 등은 실패로 집계).
- `export`: `--month YYYY-MM` **또는** `--from`/`--to` 조건을 **하나 이상 필수**로 받습니다.

---

## 6. 설계 포인트 (과제 목표 대응)

- **계층형 모듈 구조** — 책임을 4계층으로 분리:
  - `models.py` (데이터 구조 · dataclass) →
  - `repository.py` (파일 I/O) →
  - `service.py` (비즈니스 로직) →
  - `cli.py` (명령/입출력). 그 외 `decorators.py`, `errors.py`.
- **제너레이터 스트리밍** — `repository.py` 가 파일을 통째로 로드하지 않습니다.
  최신순 조회는 파일을 **뒤에서부터 블록 단위로 읽는 역방향 스트리밍**(`_read_lines_reverse`)
  으로 구현했고, `list --limit N` 은 N개만 `yield` 하고 멈춰 대용량 파일에서도 앞부분만 읽습니다.
- **데코레이터로 공통 관심사 분리** — `log_call`(호출 로그), `timed`(실행 시간 측정),
  `handle_errors`(예외 → 원인+힌트 출력, 종료 코드) 를 서비스/최상위에 실제 적용.
- **타입 힌트** — 모든 함수 시그니처와 dataclass 필드에 타입을 명시해 입출력 계약을 고정.
- **안정적 쓰기** — update/delete/budget/category 변경은 임시 파일 + `os.replace` 원자적 교체.
- **예외/종료 코드** — 스택트레이스 대신 `오류: ... / 힌트: ...` 를 출력하고,
  정상 종료 0, 오류 종료 1(입력·상태 오류)/2(예상치 못한 오류)/130(중단).

---

## 7. 프로젝트 구조

```
budget_app/
├── __init__.py
├── __main__.py      # python -m budget_app 진입점
├── cli.py           # 명령 파싱(argparse) + 대화형 입력 + 출력
├── service.py       # 비즈니스 로직 (BudgetService, SearchFilter, MonthlySummary)
├── repository.py    # 파일 I/O (TransactionRepository, CategoryStore, BudgetStore)
├── models.py        # 데이터 구조 (Transaction, Category, Budget)
├── decorators.py    # log_call / timed / handle_errors
└── errors.py        # AppError, ValidationError, NotFoundError, ConflictError
```
