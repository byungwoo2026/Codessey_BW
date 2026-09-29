"""Mini Git 실행 진입점.

`python main.py` 로 실행하면 이 파일이 mini_git 패키지의 CLI를 띄운다.
실제 로직은 전부 mini_git/ 폴더 안에 있고, 이 파일은 '시작 버튼' 역할만 한다.
"""

from __future__ import annotations
                                    
import sys

from mini_git.cli import main


if __name__ == "__main__":
    # main()이 돌려준 값을 종료 코드로 그대로 넘긴다. 0이면 정상 종료.
    sys.exit(main())
