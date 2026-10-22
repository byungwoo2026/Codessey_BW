"""Mini Git: 커밋 그래프(DAG), 브랜치, 역색인, 직접 구현한 정렬로 만든 CLI 버전 관리 흉내.

파일 지도
  models.py     커밋 데이터 모양(Commit), hash 발급기, 에러 종류
  sorting.py    병합 정렬 (내장 정렬 금지라서 직접 구현)
  graph.py      커밋 그래프 + 위상 정렬 / 조상 탐색 / 최단 경로
  index.py      역색인 (keyword -> 커밋, author -> 커밋)
  repository.py 브랜치/HEAD/커밋 생성 + 위 부품들을 묶는 지휘자
  cli.py        입력 파싱 + 출력 형식 + REPL

데이터는 한 방향으로 흐른다:  cli -> repository -> (graph / index / sorting / models)
"""
