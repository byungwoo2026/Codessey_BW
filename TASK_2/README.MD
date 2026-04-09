# 🎮 퀴즈 게임 프로젝트 - 사용 설명서

## 📍 프로젝트 위치

```
/root/quiz-game/
```

---

## 🚀 빠른 시작

### Step 1: 프로젝트 디렉토리로 이동

```bash
cd /root/quiz-game
```

### Step 2: 파일 확인

```bash
ls -la
```

**출력 예시:**
```
-rw-r--r--  main.py
-rw-r--r--  quiz_manager.py
-rw-r--r--  player_manager.py
-rw-r--r--  quizzes.json
-rw-r--r--  state.json
-rw-r--r--  README.md
-rw-r--r--  .gitignore
```

### Step 3: 게임 실행

```bash
python main.py
```

### Step 4: 플레이어 이름 입력

```
👤 플레이어 이름을 입력하세요: 홍길동
```

### Step 5: 퀴즈 풀기

```
📝 문제 1: Python에서 리스트를 생성하는 방법은?
   1. list()
   2. []
   3. {}
   답변 (1-3): 2
```

### Step 6: 결과 확인

```
✅ 정답입니다! (+10점)
```

### Step 7: 최종 점수

```
🏆 게임 완료! 최종 점수: 30점
```

---

## 📁 파일 설명

### main.py
**역할:** 게임의 메인 로직
- 플레이어 이름 입력
- 퀴즈 출제
- 답변 채점
- 점수 계산

**실행:**
```bash
python main.py
```

### quiz_manager.py
**역할:** 퀴즈 데이터 관리
- JSON 파일에서 퀴즈 로드
- 특정 퀴즈 조회
- 정답 확인

**클래스:**
```python
class QuizManager:
    - load_quizzes()      # 퀴즈 로드
    - get_quiz(id)        # 특정 퀴즈 조회
    - get_all_quizzes()   # 모든 퀴즈 조회
    - check_answer()      # 정답 확인
```

### player_manager.py
**역할:** 플레이어 정보 관리
- 플레이어 생성
- 점수 업데이트
- 게임 상태 저장

**클래스:**
```python
class PlayerManager:
    - create_player()     # 플레이어 생성
    - update_score()      # 점수 업데이트
    - get_player_score()  # 점수 조회
    - get_all_players()   # 모든 플레이어 조회
```

### quizzes.json
**역할:** 퀴즈 데이터 저장
**형식:** JSON

**예시:**
```json
{
  "quizzes": [
    {
      "id": 1,
      "question": "질문",
      "options": ["선택지1", "선택지2", "선택지3"],
      "correct_answer": 1
    }
  ]
}
```

**퀴즈 추가 방법:**
1. quizzes.json 파일 열기
2. 새로운 퀴즈 객체 추가
3. id, question, options, correct_answer 입력
4. 파일 저장

### state.json
**역할:** 게임 상태 저장
**형식:** JSON

**예시:**
```json
{
  "players": {
    "홍길동": {
      "score": 30,
      "quizzes_solved": [1, 2, 3]
    }
  },
  "current_player": null
}
```

### README.md
**역할:** 프로젝트 설명 문서

### .gitignore
**역할:** Git에서 무시할 파일 목록

---

## 🎮 게임 플레이 예시

### 예시 1: 완벽한 점수

```bash
$ python main.py
==================================================
🎮 퀴즈 게임에 오신 것을 환영합니다!
==================================================

👤 플레이어 이름을 입력하세요: 김철수

✅ 3개의 퀴즈가 있습니다.

📝 문제 1: Python에서 리스트를 생성하는 방법은?
   1. list()
   2. []
   3. {}
   답변 (1-3): 2
   ✅ 정답입니다! (+10점)

📝 문제 2: 다음 중 불변 자료형은?
   1. list
   2. tuple
   3. dict
   답변 (1-3): 2
   ✅ 정답입니다! (+10점)

📝 문제 3: Python의 반복문은?
   1. for
   2. while
   3. 모두 맞음
   답변 (1-3): 3
   ✅ 정답입니다! (+10점)

==================================================
🏆 게임 완료! 최종 점수: 30점
==================================================
```

### 예시 2: 부분 정답

```bash
$ python main.py
==================================================
🎮 퀴즈 게임에 오신 것을 환영합니다!
==================================================

👤 플레이어 이름을 입력하세요: 이영희

✅ 3개의 퀴즈가 있습니다.

📝 문제 1: Python에서 리스트를 생성하는 방법은?
   1. list()
   2. []
   3. {}
   답변 (1-3): 1
   ❌ 틀렸습니다. 정답: []

📝 문제 2: 다음 중 불변 자료형은?
   1. list
   2. tuple
   3. dict
   답변 (1-3): 2
   ✅ 정답입니다! (+10점)

📝 문제 3: Python의 반복문은?
   1. for
   2. while
   3. 모두 맞음
   답변 (1-3): 2
   ❌ 틀렸습니다. 정답: 모두 맞음

==================================================
🏆 게임 완료! 최종 점수: 10점
==================================================
```

---

## 📊 게임 규칙

| 항목 | 설명 |
|------|------|
| **총 퀴즈 수** | 3개 |
| **정답 점수** | 10점 |
| **오답 점수** | 0점 |
| **최대 점수** | 30점 |
| **시간 제한** | 없음 |

---

## 🔧 커스터마이징

### 1. 퀴즈 추가하기

**quizzes.json 파일 수정:**

```json
{
  "quizzes": [
    {
      "id": 1,
      "question": "Python에서 리스트를 생성하는 방법은?",
      "options": ["list()", "[]", "{}"],
      "correct_answer": 1
    },
    {
      "id": 4,
      "question": "새로운 질문?",
      "options": ["선택지1", "선택지2", "선택지3"],
      "correct_answer": 0
    }
  ]
}
```

### 2. 점수 변경하기

**player_manager.py 파일 수정:**

```python
# 기존 코드
if is_correct:
    self.state['players'][name]['score'] += 10

# 변경 (예: 20점으로 변경)
if is_correct:
    self.state['players'][name]['score'] += 20
```

### 3. 게임 메시지 변경하기

**main.py 파일 수정:**

```python
# 기존 코드
print("🎮 퀴즈 게임에 오신 것을 환영합니다!")

# 변경
print("🎮 Python 퀴즈 게임에 오신 것을 환영합니다!")
```

---

## 🐛 문제 해결

### 문제 1: "ModuleNotFoundError: No module named 'quiz_manager'"

**원인:** 프로젝트 디렉토리에서 실행하지 않음

**해결:**
```bash
cd /root/quiz-game
python main.py
```

### 문제 2: "FileNotFoundError: quizzes.json"

**원인:** quizzes.json 파일이 없음

**해결:**
```bash
# 파일 확인
ls -la quizzes.json

# 파일이 없으면 다시 생성
cat > quizzes.json << 'EOF'
{
  "quizzes": [
    {
      "id": 1,
      "question": "Python에서 리스트를 생성하는 방법은?",
      "options": ["list()", "[]", "{}"],
      "correct_answer": 1
    }
  ]
}
EOF
```

### 문제 3: 게임이 실행되지 않음

**해결:**
```bash
# Python 버전 확인
python --version

# Python 3 사용
python3 main.py

# 파일 권한 확인
ls -la *.py

# 파일 내용 확인
cat main.py
```

---

## 📈 게임 진행 상황 확인

### 플레이어 점수 확인

```bash
cat state.json
```

**출력 예시:**
```json
{
  "players": {
    "홍길동": {
      "score": 30,
      "quizzes_solved": [1, 2, 3]
    },
    "김철수": {
      "score": 20,
      "quizzes_solved": [1, 2]
    }
  },
  "current_player": null
}
```

### 퀴즈 데이터 확인

```bash
cat quizzes.json
```

### 프로젝트 구조 확인

```bash
tree quiz-game
# 또는
find . -type f
```

---

## 💡 확장 아이디어

### 1. 난이도 선택 기능
```python
# 쉬움, 보통, 어려움 난이도별 퀴즈 분류
```

### 2. 시간 제한 기능
```python
# 각 문제마다 제한 시간 설정
```

### 3. 랭킹 시스템
```python
# 플레이어 점수 순위 표시
```

### 4. 카테고리별 퀴즈
```python
# Python, JavaScript, HTML 등 카테고리 분류
```

### 5. 다중 플레이어 모드
```python
# 여러 플레이어가 동시에 게임 진행
```

### 6. GUI 인터페이스
```python
# tkinter, PyQt 등으로 GUI 구현
```

---

## 📚 학습 포인트

### 1. 클래스 설계
- QuizManager: 퀴즈 관리
- PlayerManager: 플레이어 관리

### 2. JSON 처리
- JSON 파일 읽기/쓰기
- 데이터 구조화

### 3. 파일 I/O
- 파일 생성, 읽기, 수정
- 예외 처리

### 4. 사용자 입력 처리
- input() 함수 사용
- 입력 검증

### 5. 게임 로직
- 점수 계산
- 상태 관리

---

## ✅ 체크리스트

게임을 완벽하게 실행하기 위한 체크리스트:

- [ ] 프로젝트 디렉토리 확인: `/root/quiz-game/`
- [ ] 파일 목록 확인: `ls -la`
- [ ] main.py 실행: `python main.py`
- [ ] 플레이어 이름 입력
- [ ] 3개 퀴즈 모두 풀기
- [ ] 최종 점수 확인
- [ ] state.json 파일 확인: `cat state.json`
- [ ] 다시 게임 실행하여 플레이어 기록 확인

---

## 🎓 다음 단계

1. **Git 저장소 초기화**
   ```bash
   cd /root/quiz-game
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **새로운 기능 추가**
   - 난이도 선택
   - 시간 제한
   - 랭킹 시스템

3. **테스트 코드 작성**
   - unittest 사용
   - 각 함수 테스트

4. **문서화**
   - 함수별 docstring 추가
   - 사용 예시 추가

---

## 📞 도움말

**문제가 발생했을 때:**

1. 에러 메시지 확인
2. 파일 존재 여부 확인
3. 파일 내용 확인
4. 파일 권한 확인
5. Python 버전 확인

**명령어:**
```bash
# 에러 메시지 확인
python main.py 2>&1

# 파일 확인
ls -la

# 파일 내용 확인
cat main.py

# 파일 권한 확인
stat main.py

# Python 버전 확인
python --version
```

---

**즐거운 게임되세요!** 🎮✨

