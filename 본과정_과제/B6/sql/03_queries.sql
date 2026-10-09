-- ============================================================================
-- 03_queries.sql : 핵심 쿼리 15개
--
--   분류            쿼리 번호
--   기본 조회  4개   Q1  ~ Q4   (WHERE / ORDER BY / LIMIT / LIKE / 날짜 비교)
--   조인       4개   Q5  ~ Q8   (INNER JOIN 2개 + LEFT JOIN 2개)
--   집계       3개   Q9  ~ Q11  (COUNT / AVG / SUM + GROUP BY + HAVING)
--   서브쿼리   1개   Q12
--   수정·삭제  2개   Q13 (UPDATE), Q14 (DELETE)
--   인덱스     1개   Q15
--
-- ※ 각 쿼리 맨 위의 "-- Qn. [분류] ..." 한 줄이 "무엇을 확인하는 쿼리인지" 설명이다.
-- ※ Q13 · Q14 는 데이터를 실제로 바꾼다. 그래서 반드시 Q1 → Q15 순서로 실행해야 결과가 재현된다.
--   (다시 처음부터 하고 싶으면 01_schema.sql → 02_insert_data.sql 을 먼저 다시 실행)
-- ※ 오늘 날짜는 결과가 항상 같도록 '2026-10-08' 로 고정해서 썼다.
-- ============================================================================

PRAGMA foreign_keys = ON;   -- [SQLite 전용] FK 검사 켜기


-- ############################################################################
-- A. 기본 조회 (4개)
-- ############################################################################

-- Q1. [기본 조회] 정가 20,000원 이상인 도서를 비싼 순서로 5권만 보기  (WHERE + ORDER BY + LIMIT)
SELECT book_id, title, author, price
FROM book
WHERE price >= 20000
ORDER BY price DESC, title
LIMIT 5;

-- Q2. [기본 조회] 제목에 '파이썬'이 들어간 도서 검색  (LIKE 와 % 와일드카드)
SELECT book_id, title, author, price
FROM book
WHERE title LIKE '%파이썬%'
ORDER BY title;

-- Q3. [기본 조회] 최근 30일(기준일 2026-10-08) 안에 시작된 대여 기록을 최신순으로 10건  (날짜 조건)
-- [SQLite 전용] date('2026-10-08', '-30 day') = 기준일에서 30일 전 날짜
--               (실제 서비스라면 오늘 날짜를 뜻하는 'now' 를 쓴다 : date('now', '-30 day'))
SELECT rental_id, member_id, book_id, rented_at, status
FROM rental
WHERE rented_at >= date('2026-10-08', '-30 day')
ORDER BY rented_at DESC, rental_id DESC
LIMIT 10;

-- Q4. [기본 조회] 지금 '대여 중(RENTED)'인 기록을 반납 예정일이 빠른 순으로 5건  (곧 반납해야 할 순서)
SELECT rental_id, member_id, book_id, rented_at, due_date
FROM rental
WHERE status = 'RENTED'
ORDER BY due_date, rental_id
LIMIT 5;


-- ############################################################################
-- B. 조인 (4개) : 여러 테이블에 흩어진 데이터를 FK 로 연결해서 한 번에 보기
-- ############################################################################

-- Q5. [INNER JOIN] 도서 목록에 분류 이름을 붙여서 보기  (book + category)
--     INNER JOIN = 양쪽 테이블에 짝이 있는 행만 남긴다.
SELECT b.book_id, b.title, c.name AS category, b.price
FROM book AS b
INNER JOIN category AS c ON c.category_id = b.category_id
ORDER BY c.category_id, b.book_id;

-- Q6. [INNER JOIN · 3개 테이블] 현재 대여 중인 책 목록 : 누가 · 어떤 책을 · 언제까지  (rental + member + book)
SELECT r.rental_id, m.name AS member_name, b.title, r.rented_at, r.due_date
FROM rental AS r
INNER JOIN member AS m ON m.member_id = r.member_id
INNER JOIN book   AS b ON b.book_id   = r.book_id
WHERE r.status = 'RENTED'
ORDER BY r.due_date, r.rental_id;

-- Q7. [LEFT JOIN] 한 번도 대여된 적 없는 도서 찾기  (book 기준 LEFT JOIN + 짝이 없으면 NULL)
--     LEFT JOIN = 왼쪽(book)은 전부 남기고, 오른쪽(rental)에 짝이 없으면 NULL 로 채운다.
--     그래서 "r.rental_id IS NULL" = 짝이 없다 = 한 번도 안 빌려졌다.
SELECT b.book_id, b.title, b.author
FROM book AS b
LEFT JOIN rental AS r ON r.book_id = b.book_id
WHERE r.rental_id IS NULL
ORDER BY b.book_id;

-- Q8. [LEFT JOIN + COUNT] 회원별 대여 횟수  (대여 기록이 0건인 회원도 함께 표시)
--     ※ COUNT(*) 가 아니라 COUNT(r.rental_id) 를 쓴 이유 : 짝이 없는 회원도 행이 1줄 생기는데,
--       COUNT(*) 는 그 줄을 1건으로 세어 버리고 COUNT(컬럼) 은 NULL 을 빼고 세어서 0 이 나온다.
SELECT m.member_id, m.name, COUNT(r.rental_id) AS rental_count
FROM member AS m
LEFT JOIN rental AS r ON r.member_id = m.member_id
GROUP BY m.member_id, m.name
ORDER BY rental_count DESC, m.member_id;


-- ############################################################################
-- C. 집계 (3개) : GROUP BY 로 묶어서 COUNT / AVG / SUM 계산
-- ############################################################################

-- Q9. [집계 · COUNT, AVG] 분류별 도서 수와 평균 가격  (많은 분류 순)
SELECT c.name AS category,
       COUNT(b.book_id)                  AS book_count,
       CAST(ROUND(AVG(b.price)) AS INTEGER) AS avg_price
FROM category AS c
INNER JOIN book AS b ON b.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY book_count DESC, avg_price DESC;

-- Q10. [집계 · COUNT] 가장 많이 대여된 인기 도서 TOP 5  (JOIN + GROUP BY + ORDER BY + LIMIT)
SELECT b.title, COUNT(*) AS rental_count
FROM rental AS r
INNER JOIN book AS b ON b.book_id = r.book_id
GROUP BY b.book_id, b.title
ORDER BY rental_count DESC, b.title
LIMIT 5;

-- Q11. [집계 · SUM + HAVING] 연체료 합계가 1,500원 이상인 회원  (많은 순)
--      WHERE = 묶기 "전"에 행을 거른다 (연체료가 있는 기록만)
--      HAVING = 묶은 "후"에 그룹을 거른다 (합계가 1,500원 이상인 회원만)
SELECT m.member_id, m.name,
       COUNT(*)        AS late_count,
       SUM(r.late_fee) AS total_late_fee
FROM rental AS r
INNER JOIN member AS m ON m.member_id = r.member_id
WHERE r.late_fee > 0
GROUP BY m.member_id, m.name
HAVING SUM(r.late_fee) >= 1500
ORDER BY total_late_fee DESC;


-- ############################################################################
-- D. 서브쿼리 (1개)
-- ############################################################################

-- Q12. [서브쿼리] 대여 기록이 한 건도 없는 회원 찾기  (WHERE ... NOT IN (SELECT ...))
--      안쪽 쿼리 : 대여 기록에 한 번이라도 등장한 회원 번호 목록
--      바깥 쿼리 : 그 목록에 "없는" 회원만 출력
--      (rental.member_id 는 NOT NULL 이라 NOT IN 이 안전하다. NULL 이 섞이면 NOT IN 은 결과가 비어 버린다.)
SELECT member_id, name, email, joined_at
FROM member
WHERE member_id NOT IN (SELECT member_id FROM rental)
ORDER BY member_id;


-- ############################################################################
-- E. 데이터 수정 · 삭제 (2개) : 실제로 데이터가 바뀐다
-- ############################################################################

-- Q13. [UPDATE] 반납 예정일이 지났는데 아직 '대여 중'인 기록을 '연체(OVERDUE)'로 바꾸고 연체료(하루 300원) 계산
-- (1) 변경 전 : 상태별 건수
SELECT status, COUNT(*) AS cnt
FROM rental
GROUP BY status
ORDER BY status;

-- (2) 변경 : 조건에 맞는 행만 수정한다.  ※ WHERE 를 빼먹으면 모든 행이 바뀐다!
-- [SQLite 전용] julianday() = 날짜를 숫자로 바꿔 날짜 차이(일수)를 계산
UPDATE rental
SET status   = 'OVERDUE',
    late_fee = CAST(julianday('2026-10-08') - julianday(due_date) AS INTEGER) * 300
WHERE status = 'RENTED'
  AND due_date < '2026-10-08';

-- (3) 변경 후 : 상태별 건수
SELECT status, COUNT(*) AS cnt
FROM rental
GROUP BY status
ORDER BY status;

-- (4) 방금 연체로 바뀐 기록 확인
SELECT rental_id, member_id, book_id, due_date, status, late_fee
FROM rental
WHERE status = 'OVERDUE'
ORDER BY rental_id;

-- Q14. [DELETE] 가입만 하고 대여 기록이 없는 12번 회원(신나래)을 탈퇴 처리(삭제)
-- (1) 삭제 전 회원 수
SELECT COUNT(*) AS member_count_before
FROM member;

-- (2) 삭제 : NOT EXISTS 조건 = "대여 기록이 있는 회원은 지우지 않는다"는 안전장치 (FK 에러 방지)
DELETE FROM member
WHERE member_id = 12
  AND NOT EXISTS (SELECT 1 FROM rental AS r WHERE r.member_id = member.member_id);

-- (3) 삭제 후 회원 수
SELECT COUNT(*) AS member_count_after
FROM member;


-- ############################################################################
-- F. 인덱스 (1개)
-- ############################################################################

-- Q15. [인덱스] rental.member_id 에 인덱스를 만들고, 조회 방식이 바뀌는 것을 확인
--      적용 이유 : rental 은 계속 쌓이는 테이블이고 "특정 회원의 대여 기록"을 자주 찾는다(JOIN·WHERE 에 member_id 사용).
--                  인덱스가 없으면 전체 행을 처음부터 끝까지 읽고(SCAN), 있으면 책 뒤 색인처럼 바로 찾아간다(SEARCH).
-- [SQLite 전용] EXPLAIN QUERY PLAN = 쿼리가 어떤 방식으로 실행되는지 보여 준다.
--               (MySQL/PostgreSQL 은 EXPLAIN 만 쓴다)
-- (1) 인덱스 만들기 전
EXPLAIN QUERY PLAN
SELECT * FROM rental WHERE member_id = 3;

-- (2) 인덱스 생성
CREATE INDEX idx_rental_member_id ON rental (member_id);

-- (3) 인덱스 만든 후 : 같은 쿼리인데 실행 방식이 SCAN → SEARCH 로 바뀐다
EXPLAIN QUERY PLAN
SELECT * FROM rental WHERE member_id = 3;
