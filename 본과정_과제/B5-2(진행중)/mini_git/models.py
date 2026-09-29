"""커밋 한 개가 어떤 정보를 담는지 정의하는 파일."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Commit:
    """Mini Git의 커밋 노드.

    커밋 하나는 그래프에서 '점(노드)' 하나에 해당한다.
    그리고 parents가 '화살표(간선)' 역할을 해서, 커밋들이 서로 연결된다.

    필드 설명
    - hash      : 커밋을 구분하는 고유 이름표. 예) "C000001"
    - message   : 커밋 메시지. 검색(SEARCH)의 재료가 된다
    - author    : 작성자 이름
    - timestamp : 만들어진 시각. LOG --sort-by=date 의 정렬 기준
    - parents   : 부모 커밋의 hash 목록. 이게 곧 그래프의 연결선이다
                  첫 커밋은 부모가 없어서 빈 리스트([])가 된다

    부모는 항상 '나보다 먼저 만들어진 커밋'이라서 되돌아오는 길이 생길 수 없다.
    그래서 커밋 전체 모양은 DAG(방향성 비순환 그래프)가 된다.
    """

    hash: str
    message: str
    author: str
    timestamp: str
    parents: list[str]
