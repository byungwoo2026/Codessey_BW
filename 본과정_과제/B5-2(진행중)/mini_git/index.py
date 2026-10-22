"""역색인(Inverted Index).

역색인이란?
  책 맨 뒤의 '찾아보기'와 같다. "이 단어는 몇 쪽에 나온다"를 미리 적어 둔 표.
  보통 색인은 '커밋 -> 단어들'이지만, 역색인은 거꾸로 '단어 -> 커밋들'을 저장한다.

  keyword_index = { "login": ["c002", "c005"],  "add": ["c001", "c002"], ... }
  author_index  = { "alice": ["c001", "c002"],  "bob": ["c003"], ... }

왜 빠른가?
  - 순회 검색   : 모든 커밋의 메시지를 하나씩 열어 본다           -> O(N)  (N=전체 커밋 수)
  - 역색인 검색 : 단어로 dict를 한 번 조회하면 후보가 바로 나온다 -> 평균 O(1) + 결과 개수 K
  대신 커밋을 만들 때 표를 갱신하는 일(쓰기 비용)을 조금 더 한다. 읽기를 빠르게 하려고
  쓰기에 비용을 미리 치르는 전형적인 교환(trade-off)이다.
"""

from __future__ import annotations

from .models import Commit


class InvertedIndex:
    """키워드 -> 커밋 목록, 작성자 -> 커밋 목록 두 가지 역색인을 가진다."""

    def __init__(self) -> None:
        self._by_keyword: dict[str, list[str]] = {}
        self._by_author: dict[str, list[str]] = {}

    def add(self, commit: Commit) -> None:
        """커밋 한 개를 두 인덱스에 등록한다. COMMIT 할 때마다 호출된다.

        키워드 추출 규칙(과제 최소 기준): 메시지를 공백으로 split -> 소문자로 lower.
        같은 단어가 한 메시지에 두 번 나와도 그 커밋은 한 번만 등록한다.
        작성자도 소문자로 정규화해서 `--author=alice` 로 "Alice"를 찾을 수 있게 한다.
        """
        self._by_author.setdefault(commit.author.lower(), []).append(commit.hash)

        seen: set[str] = set()
        for token in commit.message.split():
            word = token.lower()
            if word in seen:
                continue
            seen.add(word)
            self._by_keyword.setdefault(word, []).append(commit.hash)

    def search_keyword(self, query: str) -> list[str]:
        """query의 단어를 모두 포함한 커밋 hash 목록(만든 순서).

        단어가 하나면 dict 한 번 조회로 끝난다.
        "add login"처럼 여러 단어면 각 단어의 후보 목록을 교집합(AND)한다.
        """
        words = [token.lower() for token in query.split()]
        if not words:
            return []

        result = self._by_keyword.get(words[0], [])
        for word in words[1:]:
            allowed = set(self._by_keyword.get(word, []))
            result = [h for h in result if h in allowed]
        return list(result)

    def search_author(self, name: str) -> list[str]:
        """해당 작성자가 쓴 커밋 hash 목록(만든 순서)."""
        return list(self._by_author.get(name.strip().lower(), []))

    def dump(self) -> list[str]:
        """인덱스 내용을 사람이 볼 수 있는 줄 목록으로 만든다 (INDEX 명령, 시연/디버깅용)."""
        lines = ["[keyword index]"]
        for word, hashes in self._by_keyword.items():
            lines.append(f"  {word} -> {', '.join(hashes)}")
        lines.append("[author index]")
        for name, hashes in self._by_author.items():
            lines.append(f"  {name} -> {', '.join(hashes)}")
        return lines
