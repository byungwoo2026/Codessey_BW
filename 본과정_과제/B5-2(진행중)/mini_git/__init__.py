"""Mini Git 패키지.

파일별 역할 한눈에 보기

- models.py     : 커밋 한 개의 생김새(어떤 정보를 담는지)
- hashmap.py    : 직접 만든 해시맵. 키로 값을 바로 꺼내는 서랍장
- sorting.py    : 직접 만든 정렬(merge sort). sorted()를 못 쓰니 손으로 구현
- repository.py : 커밋 그래프 + 브랜치 + 검색 인덱스를 관리하는 핵심 두뇌
- cli.py        : 사용자가 친 명령을 해석해서 repository에 넘기는 창구

데이터 흐름은 한 방향이다.
사용자 입력 -> cli.py -> repository.py -> (hashmap / sorting / models)
"""
