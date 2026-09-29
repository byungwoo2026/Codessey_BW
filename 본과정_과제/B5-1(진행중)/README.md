# Mini Redis

Redis의 핵심 동작을 학습용으로 직접 구현한 CLI 기반 Mini Redis입니다. 실제 Redis 서버에 연결하지 않고, Python 메모리 안에서 `SET`, `GET`, `DEL`, `EXPIRE`, `TTL`, LRU 제거, 메모리 사용량 계산을 직접 처리합니다.

## 실행 방법

Task4 폴더에서 실행합니다.

```powershell
cd C:\Codyssey26\본과정\Task4
python -m mini_redis
```

실행하면 아래 프롬프트가 나타납니다.

```text
mini-redis>
```

종료는 `exit` 또는 `quit`을 입력합니다.

## 명령어

### 문자열 기본 명령

```text
SET key value
GET key
DEL key
EXISTS key
DBSIZE
KEYS
```

값에 공백이 있으면 큰따옴표로 감쌀 수 있습니다.

```text
SET user:1 "Alice Kim"
GET user:1
```

### 메모리 관리

```text
CONFIG SET maxmemory 30
INFO memory
```

`maxmemory`는 바이트 단위입니다. `0`은 무제한입니다. 메모리 계산은 과제 조건대로 아래 공식만 사용합니다.

```text
used_memory = len(utf8(key)) + len(utf8(value)) 의 합
```

메모리가 초과되면 가장 오래 사용하지 않은 키부터 LRU 방식으로 삭제합니다.

### TTL 관리

```text
EXPIRE key seconds
TTL key
```

`EXPIRE`는 키의 만료 시간을 설정합니다. `TTL`은 남은 시간을 초 단위로 보여줍니다.

## 실행 예시

```text
mini-redis> CONFIG SET maxmemory 30
OK
mini-redis> SET user:1 "Alice"
OK
mini-redis> SET user:2 "Bob"
OK
mini-redis> SET user:3 "Charlie"
OK
mini-redis> GET user:1
(nil)
mini-redis> INFO memory
used_memory:22
maxmemory:30
evicted_keys:1
mini-redis> KEYS
1. "user:2"
2. "user:3"
mini-redis> EXPIRE user:2 3
(integer) 1
mini-redis> TTL user:2
(integer) 2
```

### 실습 예제 상세 설명

위 예시는 `maxmemory`를 작게 잡아 LRU 제거가 실제로 일어나는지 확인하는 흐름입니다.

1. 메모리 제한 설정

```text
mini-redis> CONFIG SET maxmemory 30
OK
```

`maxmemory`를 `30`바이트로 설정합니다. 이제 저장된 key와 value의 UTF-8 길이 합이 30바이트를 넘으면 가장 오래 사용하지 않은 key부터 삭제됩니다.

2. 첫 번째 key 저장

```text
mini-redis> SET user:1 "Alice"
OK
```

`user:1`이라는 key에 `Alice`를 저장합니다. 메모리 사용량은 key 길이와 value 길이의 합으로 계산합니다.

```text
len("user:1") + len("Alice") = 6 + 5 = 11
```

현재 저장 상태는 다음과 같습니다.

```text
user:1 = Alice
used_memory = 11
```

3. 두 번째 key 저장

```text
mini-redis> SET user:2 "Bob"
OK
```

`user:2`에 `Bob`을 저장합니다.

```text
len("user:2") + len("Bob") = 6 + 3 = 9
```

현재 총 메모리는 `11 + 9 = 20`바이트입니다. 아직 `maxmemory 30`을 넘지 않습니다.

```text
user:1 = Alice
user:2 = Bob
used_memory = 20
```

4. 세 번째 key 저장과 LRU 제거

```text
mini-redis> SET user:3 "Charlie"
OK
```

`user:3`에 `Charlie`를 저장하려고 하면 새 데이터 크기는 다음과 같습니다.

```text
len("user:3") + len("Charlie") = 6 + 7 = 13
```

기존 `used_memory`가 20이므로 그대로 추가하면 `20 + 13 = 33`바이트가 됩니다. 제한인 30바이트를 넘기 때문에 LRU 제거가 실행됩니다.

이 시점에서 가장 오래 사용하지 않은 key는 `user:1`입니다. 그래서 `user:1`이 삭제되고, `evicted_keys`가 1 증가합니다.

```text
삭제 전: user:1, user:2, user:3
LRU 제거: user:1
삭제 후: user:2, user:3
```

남은 메모리는 다음과 같습니다.

```text
user:2 = Bob      -> 9바이트
user:3 = Charlie  -> 13바이트
used_memory = 22
```

5. 삭제된 key 조회

```text
mini-redis> GET user:1
(nil)
```

`user:1`은 LRU 제거로 이미 삭제되었으므로 `(nil)`이 출력됩니다. Redis 스타일에서 `(nil)`은 “값이 없다”는 뜻입니다.

6. 메모리 정보 확인

```text
mini-redis> INFO memory
used_memory:22
maxmemory:30
evicted_keys:1
```

각 항목의 의미는 다음과 같습니다.

- `used_memory:22`는 현재 저장된 key/value의 총 크기입니다.
- `maxmemory:30`은 설정한 최대 메모리 제한입니다.
- `evicted_keys:1`은 LRU 때문에 자동 삭제된 key 개수입니다.

7. 현재 key 목록 확인

```text
mini-redis> KEYS
1. "user:2"
2. "user:3"
```

`user:1`은 제거되었기 때문에 보이지 않고, 현재 남아 있는 `user:2`, `user:3`만 출력됩니다.

8. TTL 설정

```text
mini-redis> EXPIRE user:2 3
(integer) 1
```

`user:2`가 3초 뒤에 만료되도록 설정합니다. `(integer) 1`은 만료 시간 설정에 성공했다는 뜻입니다. 만약 없는 key에 `EXPIRE`를 실행하면 `(integer) 0`이 나옵니다.

9. 남은 TTL 확인

```text
mini-redis> TTL user:2
(integer) 2
```

`user:2`의 만료까지 남은 시간을 초 단위로 보여줍니다. 실행하는 순간의 시간 차이 때문에 결과는 `3`, `2`, `1`처럼 조금 달라질 수 있습니다.

3초가 지난 뒤 다시 조회하면 `user:2`는 만료되어 삭제됩니다.

```text
mini-redis> GET user:2
(nil)
mini-redis> TTL user:2
(integer) -2
```

`TTL` 결과에서 `-2`는 key가 없다는 뜻이고, `-1`은 key는 있지만 만료 시간이 없다는 뜻입니다.

## 프로젝트 구조

```text
mini_redis/
├── __init__.py       패키지 표시
├── __main__.py       python -m mini_redis 실행 진입점
├── cli.py            REPL, 명령어 파싱, Redis 스타일 출력
├── store.py          SET/GET/TTL/LRU/메모리 제한 업무 로직
├── hashmap.py        직접 구현한 체이닝 방식 해시맵
├── linked_list.py    직접 구현한 이중 연결 리스트
└── min_heap.py       직접 구현한 최소 힙
```

## 모듈별 책임

| 모듈 | 책임 |
| --- | --- |
| `cli.py` | 사용자가 입력한 문자열 명령을 파싱하고 결과를 출력합니다 |
| `store.py` | Redis 명령의 실제 동작, LRU, TTL, 메모리 제한을 조합합니다 |
| `hashmap.py` | `dict` 대신 사용할 해시맵을 직접 구현합니다 |
| `linked_list.py` | 최근 사용 순서를 관리하기 위한 이중 연결 리스트를 구현합니다 |
| `min_heap.py` | 가장 빨리 만료될 TTL을 찾기 위한 최소 힙을 구현합니다 |
| `__main__.py` | `python -m mini_redis` 실행 시 `cli.main()`을 호출합니다 |

### 모듈별 상세 설명

#### `__init__.py`

`mini_redis` 폴더를 파이썬 패키지로 인식하게 만드는 파일입니다. 코드 실행보다는 “이 폴더는 import 가능한 패키지다”라고 알려주는 역할을 합니다.

이 파일이 있으면 아래처럼 패키지 단위 실행과 import가 가능합니다.

```powershell
python -m mini_redis
```

```python
from mini_redis.store import MiniRedis
```

#### `__main__.py`

`python -m mini_redis`를 실행했을 때 가장 먼저 실행되는 진입점입니다. 직접 명령어를 처리하지 않고, `cli.py`의 `main()` 함수를 호출합니다.

실행 흐름은 다음과 같습니다.

```text
python -m mini_redis
        ↓
mini_redis/__main__.py
        ↓
cli.main()
        ↓
REPL 실행
```

이렇게 분리하면 실행 시작점은 짧게 유지하고, 실제 CLI 로직은 `cli.py`에 모아둘 수 있습니다.

#### `cli.py`

사용자가 입력한 명령어를 읽고 해석하는 모듈입니다. 예를 들어 사용자가 아래처럼 입력하면:

```text
SET user:1 "Alice"
```

`cli.py`는 이 문자열을 `SET`, `user:1`, `Alice`로 나눈 뒤 `store.set("user:1", "Alice")`를 호출합니다.

주요 책임은 다음과 같습니다.

- `mini-redis>` 프롬프트를 반복 출력합니다.
- `SET`, `GET`, `DEL` 같은 명령어 이름을 구분합니다.
- 명령어 인자 개수가 맞는지 확인합니다.
- 잘못된 명령어에 Redis 스타일 오류를 출력합니다.
- 큰따옴표로 감싼 값, 예를 들어 `"Alice Kim"`을 하나의 값으로 처리합니다.

`cli.py`는 데이터를 직접 저장하지 않습니다. 실제 저장, 조회, 삭제는 `store.py`의 `MiniRedis` 객체에게 맡깁니다.

#### `store.py`

Mini Redis의 중심 모듈입니다. 사용자가 입력한 Redis 명령이 실제로 어떤 자료구조를 건드려야 하는지 결정합니다.

예를 들어 `SET user:1 "Alice"`가 들어오면 `store.py`는 다음 일을 처리합니다.

```text
1. 만료된 key가 있는지 먼저 정리
2. user:1 + Alice의 메모리 크기 계산
3. 해시맵에 값 저장
4. 기존 TTL 제거
5. LRU 순서를 최신으로 갱신
6. maxmemory 초과 시 오래된 key 제거
```

`store.py`가 관리하는 내부 자료구조는 다음과 같습니다.

- `_data`: key와 value를 저장하는 해시맵입니다.
- `_lru`: 최근 사용 순서를 저장하는 이중 연결 리스트입니다.
- `_lru_nodes`: key로 LRU 노드를 빠르게 찾기 위한 해시맵입니다.
- `_expires`: key별 만료 시간을 저장하는 해시맵입니다.
- `_expire_heap`: 가장 빨리 만료될 key를 찾기 위한 최소 힙입니다.

즉 `store.py`는 “명령어의 의미”를 담당합니다. 자료구조 자체의 세부 구현은 `hashmap.py`, `linked_list.py`, `min_heap.py`에 맡깁니다.

#### `hashmap.py`

Python의 `dict`를 쓰지 않고 key-value 저장소를 직접 구현한 모듈입니다. Redis가 빠른 이유 중 하나는 key로 값을 빠르게 찾을 수 있기 때문인데, 이 과제에서는 그 원리를 해시맵으로 직접 구현합니다.

동작 흐름은 다음과 같습니다.

```text
key 입력
  ↓
직접 만든 해시 함수로 숫자 생성
  ↓
버킷 인덱스 계산
  ↓
해당 버킷에서 key 검색
```

서로 다른 key가 같은 버킷에 들어갈 수 있습니다. 이것을 해시 충돌이라고 합니다. 이 구현에서는 충돌이 나면 `Entry` 노드를 `next`로 연결하는 체이닝 방식으로 처리합니다.

또 저장된 데이터가 많아져 로드 팩터가 0.75를 넘으면 버킷 개수를 2배로 늘립니다. 이렇게 해야 한 버킷에 데이터가 너무 많이 몰리는 것을 줄일 수 있습니다.

#### `linked_list.py`

LRU를 구현하기 위한 이중 연결 리스트 모듈입니다. LRU는 “가장 오래 사용하지 않은 key부터 삭제”하는 정책입니다.

이 리스트에서는 다음 규칙을 사용합니다.

```text
head = 가장 최근에 사용한 key
tail = 가장 오래 사용하지 않은 key
```

예를 들어 `GET user:2`가 성공하면 `user:2`는 방금 사용된 key이므로 리스트 맨 앞으로 이동합니다. 반대로 메모리가 부족하면 리스트 맨 뒤의 key를 삭제합니다.

이중 연결 리스트를 쓰는 이유는 중간 노드를 삭제하거나 앞으로 옮기는 작업을 O(1)에 처리하기 위해서입니다. 단방향 리스트라면 이전 노드를 찾기 위해 다시 탐색해야 하지만, 이중 연결 리스트는 `prev`, `next`를 모두 가지고 있어 바로 연결을 바꿀 수 있습니다.

#### `min_heap.py`

TTL 만료 시간을 관리하기 위한 최소 힙 모듈입니다. TTL은 “이 key가 몇 초 뒤에 사라져야 하는가”를 의미합니다.

여러 key에 만료 시간이 있을 때, 매번 전체 key를 다 돌면서 만료 여부를 확인하면 비효율적입니다. 최소 힙을 쓰면 가장 빨리 만료될 key가 항상 맨 위에 있으므로 빠르게 확인할 수 있습니다.

동작 방식은 다음과 같습니다.

```text
EXPIRE user:2 3
  ↓
현재 시간 + 3초를 expire_at으로 계산
  ↓
(expire_at, "user:2")를 최소 힙에 push
  ↓
명령 실행 전, 힙의 맨 위가 현재 시간보다 과거이면 삭제
```

이 구현에서는 TTL을 다시 설정했을 때 힙 안의 오래된 만료 기록을 즉시 찾아 삭제하지 않습니다. 대신 `_expires`에 최신 만료 시간만 저장해두고, 나중에 힙에서 꺼낼 때 최신 값과 다르면 오래된 기록으로 보고 버립니다. 이런 방식을 lazy deletion이라고 합니다.

## 핵심 자료구조 사용 목적과 도식화

### HashMap

#### 사용 목적

`HashMap`은 Redis의 가장 기본 기능인 “key로 value를 빠르게 찾기” 위해 사용합니다. 사용자가 `GET user:1`을 입력했을 때 전체 데이터를 처음부터 끝까지 찾으면 느립니다. 해시맵은 key를 해시 함수에 넣어 바로 찾아갈 버킷 위치를 계산하므로 평균적으로 빠른 조회가 가능합니다.

Mini Redis에서는 다음 저장소들이 모두 직접 구현한 `HashMap`을 사용합니다.

- `_data`: 실제 key/value 저장
- `_lru_nodes`: key에 해당하는 LRU 노드 위치 저장
- `_expires`: key에 해당하는 만료 시각 저장

#### 동작 도식

```text
SET user:1 Alice
        │
        ▼
hash("user:1") 계산
        │
        ▼
bucket index = hash % capacity
        │
        ▼
버킷 배열

index 0   None
index 1   Entry("name", "Bob")
index 2   None
index 3   Entry("user:1", "Alice") -> Entry("user:9", "Tom")
index 4   None
```

`user:1`과 `user:9`가 같은 버킷에 들어가면 해시 충돌이 발생한 것입니다. 이때 `Entry`를 `next`로 연결해 한 줄로 이어둡니다. 이것을 체이닝 방식이라고 합니다.

조회할 때는 같은 방식으로 버킷 위치를 찾고, 그 버킷 안에서 key가 같은 `Entry`를 찾습니다.

```text
GET user:1
   │
   ▼
hash("user:1") % capacity = 3
   │
   ▼
index 3 버킷만 확인
   │
   ▼
Entry("user:1", "Alice") 발견
   │
   ▼
"Alice" 반환
```

#### 왜 필요한가

만약 해시맵이 없으면 `GET`을 할 때 모든 key를 하나씩 비교해야 합니다.

```text
user:1 찾기
  user:7? 아니오
  name? 아니오
  user:3? 아니오
  user:1? 찾음
```

데이터가 많아질수록 느려집니다. 해시맵은 key가 많아져도 버킷 위치를 바로 계산해서 접근하므로 Redis 같은 key-value 저장소의 기본 자료구조로 적합합니다.

#### 체이닝 방식 해시맵 상세 설명

해시맵은 key를 해시 함수에 넣어서 버킷 위치를 계산합니다. 하지만 버킷 개수는 제한되어 있기 때문에 서로 다른 key라도 같은 버킷 번호가 나올 수 있습니다. 이것을 해시 충돌이라고 합니다.

```text
hash("user:1") % 4 = 2
hash("name")   % 4 = 2
```

위처럼 서로 다른 key가 같은 `index 2`에 들어가야 하는 상황이 생길 수 있습니다.

체이닝 방식은 이 문제를 “같은 버킷 안에 여러 Entry를 연결해서 저장”하는 방식으로 해결합니다.

```text
버킷 배열

index 0   None
index 1   None
index 2   Entry("name", "Bob") -> Entry("user:1", "Alice") -> None
index 3   None
```

여기서 `Entry` 하나는 다음 정보를 가집니다.

```text
Entry
├── key
├── value
└── next
```

`next`는 같은 버킷에 있는 다음 Entry를 가리킵니다. 그래서 같은 버킷에 여러 key가 들어와도 한 줄로 이어둘 수 있습니다.

##### 저장 흐름

`put("user:1", "Alice")`가 들어오면 다음 순서로 동작합니다.

```text
1. "user:1"의 해시값 계산
2. 버킷 인덱스 계산
3. 해당 버킷으로 이동
4. 같은 key가 이미 있는지 체인을 따라 확인
5. 있으면 value 덮어쓰기
6. 없으면 새 Entry를 체인 앞에 연결
```

새 Entry를 체인 앞에 연결하는 모습은 다음과 같습니다.

```text
기존 상태

index 2   Entry("name", "Bob") -> None

put("user:1", "Alice") 이후

index 2   Entry("user:1", "Alice") -> Entry("name", "Bob") -> None
```

새 노드를 앞에 붙이면 기존 체인의 모든 노드를 뒤로 밀 필요가 없습니다. 새 Entry의 `next`만 기존 첫 Entry로 연결하면 됩니다.

##### 조회 흐름

`get("name")`이 들어오면 먼저 `"name"`이 들어갈 버킷 위치를 계산합니다.

```text
get("name")
    │
    ▼
index 2 계산
    │
    ▼
Entry("user:1", "Alice") 확인
    │
    ▼
key가 다름, next로 이동
    │
    ▼
Entry("name", "Bob") 확인
    │
    ▼
key가 같음, "Bob" 반환
```

같은 버킷 안에서는 연결된 Entry를 하나씩 확인하지만, 전체 데이터를 다 보는 것은 아닙니다. 먼저 해시값으로 특정 버킷까지 좁혀놓고 그 안에서만 찾습니다.

##### 삭제 흐름

체이닝에서 삭제할 때는 이전 Entry를 기억해야 합니다. 중간 Entry를 지우면 앞 Entry의 `next`를 뒤 Entry로 다시 연결해야 하기 때문입니다.

```text
삭제 전

Entry("user:1") -> Entry("name") -> Entry("age") -> None

remove("name") 이후

Entry("user:1") -> Entry("age") -> None
```

그래서 `hashmap.py`의 `remove()`는 `current`와 `previous`를 같이 사용합니다.

```text
previous = Entry("user:1")
current  = Entry("name")

삭제 시:
previous.next = current.next
```

##### 로드 팩터와 리사이즈

체인이 너무 길어지면 한 버킷 안에서 확인해야 할 Entry가 많아져 느려집니다. 그래서 해시맵은 저장된 개수와 버킷 개수의 비율을 봅니다. 이 비율을 로드 팩터라고 합니다.

```text
load_factor = 저장된 key 개수 / 버킷 개수
```

이번 구현에서는 새 값을 넣었을 때 로드 팩터가 `0.75`를 넘으면 버킷 개수를 2배로 늘립니다.

```text
버킷 4개, key 3개  -> load_factor = 3 / 4 = 0.75
새 key 추가 예정   -> 4 / 4 = 1.0
0.75 초과          -> 버킷을 8개로 확장
```

버킷 개수가 바뀌면 `hash(key) % capacity` 결과도 달라질 수 있습니다. 그래서 기존 Entry들을 새 버킷 배열에 다시 배치해야 합니다. 이것을 리해싱이라고 볼 수 있습니다.

```text
확장 전 capacity = 4
hash("user:1") % 4 = 2

확장 후 capacity = 8
hash("user:1") % 8 = 6
```

즉 리사이즈 후에는 기존 key들이 다른 버킷으로 이동할 수 있습니다.

### DoublyLinkedList

#### 사용 목적

`DoublyLinkedList`는 LRU를 구현하기 위해 사용합니다. LRU는 메모리가 부족할 때 “가장 오래 사용하지 않은 key”를 먼저 삭제하는 정책입니다.

Mini Redis에서는 다음 규칙으로 사용합니다.

```text
head = 가장 최근에 사용한 key
tail = 가장 오래 사용하지 않은 key
```

`SET` 또는 `GET`으로 key가 사용되면 그 key를 리스트의 맨 앞으로 옮깁니다. 메모리가 초과되면 리스트의 맨 뒤 key를 삭제합니다.

#### 동작 도식

처음에 세 key가 저장되었다고 가정합니다.

```text
head                                      tail
 ▼                                         ▼
[user:3] <-> [user:2] <-> [user:1]
  최신                         가장 오래 사용 안 함
```

여기서 `GET user:1`을 실행하면 `user:1`은 방금 사용한 key가 됩니다. 따라서 맨 앞으로 이동합니다.

```text
GET user:1 실행 후

head                                      tail
 ▼                                         ▼
[user:1] <-> [user:3] <-> [user:2]
  최신                         가장 오래 사용 안 함
```

이 상태에서 메모리가 초과되면 tail에 있는 `user:2`가 제거됩니다.

```text
LRU 제거

삭제 대상: tail = user:2

head                         tail
 ▼                            ▼
[user:1] <-> [user:3]
```

#### 왜 이중 연결 리스트인가

단방향 리스트는 이전 노드를 모르기 때문에 중간 노드를 삭제하거나 앞으로 옮기려면 앞에서부터 다시 찾아야 합니다. 하지만 이중 연결 리스트는 각 노드가 `prev`, `next`를 모두 가지고 있습니다.

```text
이전 노드      현재 노드      다음 노드
  prev  <---  [user:2]  --->  next
```

그래서 노드 위치만 알고 있으면 연결만 바꿔 O(1)에 제거하거나 이동할 수 있습니다. Mini Redis는 `_lru_nodes` 해시맵에 `key -> Node`를 저장해두기 때문에, key만 알면 LRU 노드를 바로 찾아 이동할 수 있습니다.

```text
_lru_nodes HashMap

"user:1" -> Node(user:1)
"user:2" -> Node(user:2)
"user:3" -> Node(user:3)
```

### MinHeap

#### 사용 목적

`MinHeap`은 TTL 만료 시간을 관리하기 위해 사용합니다. TTL은 key가 자동으로 사라질 시간을 의미합니다.

예를 들어 아래 명령은 `user:2`를 3초 뒤 만료시키라는 뜻입니다.

```text
EXPIRE user:2 3
```

여러 key에 TTL이 걸려 있을 때 매번 모든 key를 검사하면 비효율적입니다. 최소 힙은 가장 작은 값이 항상 맨 위에 있으므로, 가장 먼저 만료될 key를 빠르게 확인할 수 있습니다.

#### 동작 도식

다음과 같이 TTL이 설정되었다고 가정합니다.

```text
user:2 -> 3초 뒤 만료
user:5 -> 10초 뒤 만료
user:1 -> 5초 뒤 만료
```

힙에는 `(expire_at, key)` 형태로 들어갑니다.

```text
          (3초뒤, user:2)
             /        \
   (10초뒤, user:5)  (5초뒤, user:1)
```

가장 빨리 만료되는 `(3초뒤, user:2)`가 루트에 있습니다. 명령이 실행될 때마다 루트만 먼저 확인하면 됩니다.

```text
현재 시간 확인
   │
   ▼
heap.peek()
   │
   ▼
가장 빠른 만료 시간이 현재 시간보다 지났나?
   │
   ├─ 예: pop 후 해당 key 삭제
   └─ 아니오: 아직 만료된 key 없음
```

#### TTL 재설정과 lazy deletion

같은 key에 TTL을 다시 설정하면 힙 안에 예전 만료 기록이 남아 있을 수 있습니다.

```text
EXPIRE user:2 3
EXPIRE user:2 10
```

그러면 힙에는 이런 식으로 두 기록이 있을 수 있습니다.

```text
(3초뒤, user:2)   오래된 기록
(10초뒤, user:2)  최신 기록
```

힙 중간에 있는 오래된 기록을 즉시 찾아 지우려면 복잡합니다. 그래서 Mini Redis는 `_expires` 해시맵에 최신 만료 시간만 저장합니다.

```text
_expires HashMap

"user:2" -> 10초뒤
```

나중에 힙에서 `(3초뒤, user:2)`가 나와도 `_expires`의 최신 값과 다르면 오래된 기록이므로 무시합니다. 이 방식을 lazy deletion이라고 합니다.

## 왜 이렇게 나누었나

Redis가 빠른 이유를 이해하려면 기능별로 어떤 자료구조가 쓰이는지 분리해서 보는 것이 좋습니다. 그래서 해시맵, 이중 연결 리스트, 힙을 각각 독립 모듈로 나누었습니다.

`HashMap`은 키로 값을 빠르게 찾는 역할을 합니다. `DoublyLinkedList`는 가장 최근 사용한 키를 앞에 두고, 가장 오래 사용하지 않은 키를 뒤에 두어 LRU 제거를 쉽게 만듭니다. `MinHeap`은 가장 먼저 만료될 키를 빠르게 확인하기 위해 사용합니다.

`store.py`는 이 자료구조들을 조합합니다. 예를 들어 `GET`에 성공하면 LRU 순서를 갱신하고, `SET`은 메모리 사용량을 계산한 뒤 초과하면 오래된 키를 제거합니다. `EXPIRE`는 만료 시간을 해시맵과 힙에 함께 기록하고, 만료된 키는 명령 실행 전에 삭제합니다.

## 구현 제약

학습 목적에 맞춰 `dict`, `set`, `collections`로 해시맵이나 캐시를 대체하지 않았습니다. 버킷 배열, 체이닝 노드, 리스트 노드, 힙 배열을 직접 다룹니다.

데이터 영속성은 구현하지 않습니다. 프로그램을 종료하면 저장된 키는 사라집니다.

