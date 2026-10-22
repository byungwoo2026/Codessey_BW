"""Mini Git이 공통으로 쓰는 '데이터 모양'과 '에러 종류'를 정의한다.

- Commit        : 커밋 한 개 (그래프의 점 하나)
- HashGenerator : 겹치지 않는 커밋 hash를 발급하는 기계
- MiniGitError  : 사용자에게 그대로 보여줄 에러 메시지를 실어 나르는 예외
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class MiniGitError(Exception):
    """사용자 입력이 잘못됐을 때 던지는 예외.

    예외 메시지가 곧 화면에 출력되는 문장이다.
    표준 메시지 예) "Invalid args", "Unknown branch: dev", "Unknown commit: c999"
    """


@dataclass
class Commit:
    """커밋 노드. 그래프에서 '점' 하나에 해당한다.

    필수 필드 5개 (과제 요구사항)
    - hash      : 커밋의 고유 이름표. 예) "c001"
    - message   : 커밋 메시지. 검색(SEARCH)의 재료
    - author    : 작성자 이름
    - timestamp : 커밋을 만든 시각 (datetime). LOG --sort-by=date 의 기준
    - parents   : 부모 커밋 hash 목록. 이것이 그래프의 '화살표(간선)'다.
                  첫 커밋은 부모가 없어서 빈 리스트 [] 다.
    """

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: list[str] = field(default_factory=list)


class HashGenerator:
    """세션 내에서 절대 겹치지 않는 커밋 hash를 발급한다.

    방식: 증가 카운터. c001, c002, c003, ...
    카운터는 1씩 늘기만 하고 줄지 않으므로 같은 번호가 두 번 나올 수 없다.
    (INIT을 다시 해도 이 발급기는 유지되므로, 세션 전체에서 유일하다.)

    진짜 Git은 커밋 내용을 SHA-1로 계산한 해시를 쓴다.
    여기서는 '유일성 보장'과 '직접 입력하기 쉬움'을 위해 카운터를 택했다.
    """

    def __init__(self) -> None:
        self._counter = 0

    def next_hash(self) -> str:
        """다음 hash를 발급한다. 1000번째부터는 c1000처럼 자릿수가 늘어난다."""
        self._counter += 1
        return f"c{self._counter:03d}"
