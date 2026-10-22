"""Mini Git 실행 파일.

    python main.py

실제 로직은 mini_git/ 패키지 안에 있고, 이 파일은 '시작 버튼' 역할만 한다.
"""

from mini_git.cli import run_repl

if __name__ == "__main__":
    run_repl()
