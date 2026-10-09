-- ============================================================================
-- 01_schema.sql : "도서 대여" 데이터베이스 스키마 생성 스크립트
-- DB 엔진 : SQLite 3 (파일 기반, 별도 서버 불필요)
--
-- 테이블 4개 / 1:N 관계 3개
--   category (1) ──< (N) book        : 한 카테고리에 여러 도서
--   member   (1) ──< (N) rental      : 한 회원이 여러 번 대여
--   book     (1) ──< (N) rental      : 한 도서가 여러 번 대여됨
--   (rental 은 member 와 book 을 이어 주는 "대여 기록" 테이블)
--
-- 실행 순서 : 01_schema.sql → 02_insert_data.sql → 03_queries.sql
-- ============================================================================

-- [SQLite 전용] SQLite 는 기본값이 FK 검사 OFF 이므로, 연결(접속)할 때마다 켜 줘야 한다.
--               이 줄이 없으면 "없는 회원 번호"로 대여 기록을 넣어도 에러 없이 들어가 버린다.
PRAGMA foreign_keys = ON;

-- 다시 실행해도 에러가 나지 않도록, 자식 테이블 → 부모 테이블 순서로 먼저 지운다.
DROP TABLE IF EXISTS rental;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS category;


-- ----------------------------------------------------------------------------
-- 1) category : 도서 분류 (부모 테이블)
-- ----------------------------------------------------------------------------
CREATE TABLE category (
    -- [SQLite 전용] INTEGER PRIMARY KEY AUTOINCREMENT = 번호 자동 증가 PK
    --               (MySQL: AUTO_INCREMENT / PostgreSQL: GENERATED ALWAYS AS IDENTITY)
    category_id INTEGER     PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(50) NOT NULL UNIQUE          -- 분류 이름은 비어 있으면 안 되고(NOT NULL), 중복도 안 된다(UNIQUE)
);


-- ----------------------------------------------------------------------------
-- 2) member : 도서관 회원 (부모 테이블)
-- ----------------------------------------------------------------------------
CREATE TABLE member (
    member_id INTEGER      PRIMARY KEY AUTOINCREMENT,
    name      VARCHAR(50)  NOT NULL,
    email     VARCHAR(100) NOT NULL UNIQUE,          -- 같은 이메일로 두 번 가입할 수 없다
    phone     VARCHAR(20),                           -- 비워 둘 수 있는 컬럼 (NULL 허용)
    -- [SQLite 전용] SQLite 에는 진짜 DATE 타입이 없어 'YYYY-MM-DD' 문자열로 저장된다.
    --               (이 형식은 문자열 비교만으로도 날짜 순서가 맞게 비교된다)
    joined_at DATE         NOT NULL
);


-- ----------------------------------------------------------------------------
-- 3) book : 도서 (category 의 자식, rental 의 부모)
-- ----------------------------------------------------------------------------
CREATE TABLE book (
    book_id        INTEGER      PRIMARY KEY AUTOINCREMENT,
    category_id    INTEGER      NOT NULL,            -- FK : 이 책이 속한 분류
    title          VARCHAR(200) NOT NULL,
    author         VARCHAR(100) NOT NULL,
    isbn           VARCHAR(20)  UNIQUE,              -- 도서 고유번호 (같은 ISBN 두 번 등록 불가)
    price          INTEGER      NOT NULL,            -- 정가(원)
    published_year INTEGER,

    CONSTRAINT ck_book_price CHECK (price >= 0),     -- 가격이 음수면 거부
    CONSTRAINT fk_book_category
        FOREIGN KEY (category_id) REFERENCES category (category_id)
        ON DELETE RESTRICT                           -- 책이 남아 있는 분류는 삭제 불가
);


-- ----------------------------------------------------------------------------
-- 4) rental : 대여 기록 (member 와 book 의 자식) ← 가장 많이 JOIN 되는 테이블
-- ----------------------------------------------------------------------------
CREATE TABLE rental (
    rental_id   INTEGER     PRIMARY KEY AUTOINCREMENT,
    member_id   INTEGER     NOT NULL,                -- FK : 누가 빌렸나
    book_id     INTEGER     NOT NULL,                -- FK : 어떤 책을 빌렸나
    rented_at   DATE        NOT NULL,                -- 대여일
    due_date    DATE        NOT NULL,                -- 반납 예정일
    returned_at DATE,                                -- 실제 반납일 (아직 안 돌려줬으면 NULL)
    status      VARCHAR(10) NOT NULL DEFAULT 'RENTED',   -- RENTED(대여 중) / RETURNED(반납 완료) / OVERDUE(연체)
    late_fee    INTEGER     NOT NULL DEFAULT 0,      -- 연체료(원)

    CONSTRAINT ck_rental_status CHECK (status IN ('RENTED', 'RETURNED', 'OVERDUE')),
    CONSTRAINT ck_rental_due    CHECK (due_date >= rented_at),   -- 반납 예정일이 대여일보다 앞설 수 없다
    CONSTRAINT ck_rental_fee    CHECK (late_fee >= 0),
    CONSTRAINT fk_rental_member
        FOREIGN KEY (member_id) REFERENCES member (member_id)
        ON DELETE RESTRICT,                          -- 대여 기록이 있는 회원은 삭제 불가
    CONSTRAINT fk_rental_book
        FOREIGN KEY (book_id)   REFERENCES book (book_id)
        ON DELETE RESTRICT                           -- 대여 기록이 있는 책은 삭제 불가
);
