"""패키지 실행 진입점.

Task4 폴더에서 `python -m mini_redis`를 실행하면 Python은
mini_redis/__main__.py 파일을 찾는다. 이 파일은 실제 CLI 로직을
직접 구현하지 않고, cli.py의 main() 함수만 호출한다.
"""

from __future__ import annotations

import sys

from .cli import main


if __name__ == "__main__":
    # main()이 반환한 종료 코드를 운영체제에 전달한다.
    sys.exit(main())

