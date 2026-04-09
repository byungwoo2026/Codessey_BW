import json
import os
import random


# ============================================
# ① Quiz 클래스 - 퀴즈 1개의 설계도
# ============================================
class Quiz:
    """
    개별 퀴즈를 표현하는 클래스
    - question : 문제 (문자열)
    - choices  : 선택지 4개 (리스트)
    - answer   : 정답 번호 1~4 (정수)
    """

    def __init__(self, question, choices, answer):
        self.question = question    # 문제
        self.choices = choices      # 선택지 리스트 (4개)
        self.answer = answer        # 정답 번호 (1~4)

    def display(self):
        """퀴즈 문제와 선택지를 화면에 출력"""
        print(f"\n📌 {self.question}")
        print("-" * 40)
        for i, choice in enumerate(self.choices, 1):
            print(f"  {i}. {choice}")
        print("-" * 40)

    def check_answer(self, user_answer):
        """사용자 답과 정답을 비교하여 True/False 반환"""
        return user_answer == self.answer

    def to_dict(self):
        """Quiz 객체 → 딕셔너리 (JSON 저장용)"""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }

    @staticmethod
    def from_dict(data):
        """딕셔너리 → Quiz 객체 (JSON 불러오기용)"""
        return Quiz(data["question"], data["choices"], data["answer"])


# ============================================
# ② QuizGame 클래스 - 게임 전체의 설계도
# ============================================
class QuizGame:
    """
    퀴즈 게임을 관리하는 클래스
    - quizzes    : 퀴즈 목록
    - high_score : 최고 점수
    """

    SAVE_FILE = "state.json"    # 저장 파일 이름

    def __init__(self):
        self.quizzes = []       # 퀴즈 목록
        self.high_score = 0     # 최고 점수
        self.load_state()       # 프로그램 시작 시 저장된 데이터 불러오기

        # 저장된 퀴즈가 없으면 기본 퀴즈 5개 추가
        if len(self.quizzes) == 0:
            self._add_default_quizzes()
            self.save_state()

    # ------------------------------------------
    # 기본 퀴즈 5개 (주제: 파이썬 기초)
    # ------------------------------------------
    def _add_default_quizzes(self):
        """기본 퀴즈 5개를 추가하는 메서드"""
        defaults = [
            Quiz(
                "파이썬에서 화면에 출력할 때 사용하는 함수는?",
                ["input()", "print()", "echo()", "write()"],
                2
            ),
            Quiz(
                "파이썬에서 리스트의 길이를 구하는 함수는?",
                ["size()", "count()", "len()", "length()"],
                3
            ),
            Quiz(
                "파이썬에서 정수 나눗셈의 몫을 구하는 연산자는?",
                ["/", "//", "%", "**"],
                2
            ),
            Quiz(
                "파이썬에서 여러 데이터를 순서대로 저장하는 자료형은?",
                ["dict", "set", "tuple", "list"],
                4
            ),
            Quiz(
                "파이썬에서 조건이 참일 때 실행하는 키워드는?",
                ["for", "while", "if", "def"],
                3
            ),
        ]
        self.quizzes.extend(defaults)
        print("📚 기본 퀴즈 5개가 추가되었습니다!")

    # ------------------------------------------
    # 기능 1: 퀴즈 풀기
    # ------------------------------------------
    def play_quiz(self):
        """퀴즈를 랜덤으로 출제하고 점수를 계산"""
        if len(self.quizzes) == 0:
            print("\n❌ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해주세요!")
            return

        print("\n" + "=" * 50)
        print("🎮 퀴즈 풀기 시작!")
        print("=" * 50)

        # 퀴즈를 랜덤으로 섞기
        quiz_list = self.quizzes[:]     # 원본 보호를 위해 복사
        random.shuffle(quiz_list)       # 랜덤으로 섞기

        score = 0           # 맞은 개수
        total = len(quiz_list)   # 전체 문제 수

        for idx, quiz in enumerate(quiz_list, 1):
            print(f"\n📝 문제 {idx}/{total}")
            quiz.display()

            # 사용자 입력 받기
            while True:
                try:
                    user_input = input("정답 번호를 입력하세요 (1~4): ").strip()
                    user_answer = int(user_input)
                    if 1 <= user_answer <= 4:
                        break
                    else:
                        print("⚠️ 1~4 사이의 번호를 입력해주세요!")
                except ValueError:
                    print("⚠️ 숫자를 입력해주세요!")

            # 정답 확인
            if quiz.check_answer(user_answer):
                print("✅ 정답입니다! 🎉")
                score += 1
            else:
                correct = quiz.choices[quiz.answer - 1]
                print(f"❌ 오답입니다! 정답은 {quiz.answer}번 '{correct}' 입니다.")

        # 결과 출력
        print("\n" + "=" * 50)
        print(f"🏆 결과: {total}문제 중 {score}문제 정답!")
        print(f"📊 점수: {score}/{total} ({score * 100 // total}%)")

        # 최고 점수 갱신
        if score > self.high_score:
            self.high_score = score
            self.save_state()
            print(f"🎊 새로운 최고 점수! {self.high_score}점!")
        else:
            print(f"📈 현재 최고 점수: {self.high_score}점")
        print("=" * 50)

    # ------------------------------------------
    # 기능 2: 퀴즈 추가
    # ------------------------------------------
    def add_quiz(self):
        """사용자가 새로운 퀴즈를 추가"""
        print("\n" + "=" * 50)
        print("➕ 새 퀴즈 추가")
        print("=" * 50)

        # 문제 입력
        question = input("\n문제를 입력하세요: ").strip()
        if not question:
            print("❌ 문제가 비어있습니다. 추가를 취소합니다.")
            return

        # 선택지 4개 입력
        print("선택지 4개를 입력하세요:")
        choices = []
        for i in range(1, 5):
            choice = input(f"  {i}번 선택지: ").strip()
            if not choice:
                print("❌ 선택지가 비어있습니다. 추가를 취소합니다.")
                return
            choices.append(choice)

        # 정답 번호 입력
        while True:
            try:
                answer = int(input("정답 번호를 입력하세요 (1~4): ").strip())
                if 1 <= answer <= 4:
                    break
                else:
                    print("⚠️ 1~4 사이의 번호를 입력해주세요!")
            except ValueError:
                print("⚠️ 숫자를 입력해주세요!")

        # 퀴즈 추가 및 저장
        new_quiz = Quiz(question, choices, answer)
        self.quizzes.append(new_quiz)
        self.save_state()

        print(f"\n✅ 퀴즈가 추가되었습니다! (총 {len(self.quizzes)}개)")

    # ------------------------------------------
    # 기능 3: 퀴즈 목록 보기
    # ------------------------------------------
    def view_quizzes(self):
        """등록된 모든 퀴즈 목록을 출력"""
        print("\n" + "=" * 50)
        print("📋 퀴즈 목록")
        print("=" * 50)

        if len(self.quizzes) == 0:
            print("등록된 퀴즈가 없습니다.")
            return

        for idx, quiz in enumerate(self.quizzes, 1):
            correct = quiz.choices[quiz.answer - 1]
            print(f"\n[{idx}] {quiz.question}")
            for i, choice in enumerate(quiz.choices, 1):
                marker = "✔" if i == quiz.answer else " "
                print(f"    {marker} {i}. {choice}")
            print(f"    → 정답: {quiz.answer}번 ({correct})")

        print(f"\n총 {len(self.quizzes)}개의 퀴즈가 있습니다.")

    # ------------------------------------------
    # 기능 4: 점수 확인
    # ------------------------------------------
    def view_score(self):
        """현재 최고 점수를 출력"""
        print("\n" + "=" * 50)
        print("🏆 점수 확인")
        print("=" * 50)
        print(f"  최고 점수: {self.high_score}점")
        print(f"  총 퀴즈 수: {len(self.quizzes)}개")
        if len(self.quizzes) > 0:
            percent = self.high_score * 100 // len(self.quizzes)
            print(f"  최고 정답률: {percent}%")
        print("=" * 50)

    # ------------------------------------------
    # 저장 기능: 퀴즈 + 최고 점수를 JSON 파일로 저장
    # ------------------------------------------
    def save_state(self):
        """현재 상태를 state.json에 저장"""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "high_score": self.high_score
        }
        with open(self.SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ------------------------------------------
    # 불러오기 기능: JSON 파일에서 데이터 복원
    # ------------------------------------------
    def load_state(self):
        """state.json에서 저장된 상태를 불러오기"""
        if not os.path.exists(self.SAVE_FILE):
            return

        try:
            with open(self.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes", [])]
            self.high_score = data.get("high_score", 0)
            print(f"💾 저장된 데이터를 불러왔습니다! (퀴즈 {len(self.quizzes)}개)")
        except (json.JSONDecodeError, KeyError):
            print("⚠️ 저장 파일이 손상되었습니다. 새로 시작합니다.")
            self.quizzes = []
            self.high_score = 0

    # ------------------------------------------
    # 메인 메뉴 및 실행
    # ------------------------------------------
    def show_menu(self):
        """메뉴를 화면에 출력"""
        print("\n" + "=" * 50)
        print("🧠 퀴즈 게임 프로그램")
        print("=" * 50)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 목록")
        print("  4. 점수 확인")
        print("  5. 종료")
        print("=" * 50)

    def run(self):
        """게임 메인 루프"""
        while True:
            self.show_menu()
            choice = input("메뉴 번호를 선택하세요: ").strip()

            if choice == "1":
                self.play_quiz()
            elif choice == "2":
                self.add_quiz()
            elif choice == "3":
                self.view_quizzes()
            elif choice == "4":
                self.view_score()
            elif choice == "5":
                self.save_state()
                print("\n👋 프로그램을 종료합니다. 다음에 또 만나요!")
                break
            else:
                print("\n⚠️ 1~5 사이의 번호를 입력해주세요!")


# ============================================
# ③ 프로그램 시작점
# ============================================
if __name__ == "__main__":
    game = QuizGame()
    game.run()