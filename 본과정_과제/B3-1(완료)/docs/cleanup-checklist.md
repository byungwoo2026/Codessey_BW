# 리소스 정리 체크리스트

> 실습 종료 후 아래 순서대로 삭제해야 의존성 오류 없이 정리됩니다.
> 각 항목을 실제로 확인한 뒤 체크하고, 확인 시각/스크린샷을 기록합니다.
>
> **정리 일자: 2026-10-05 (서울 리전 ap-northeast-2)** — 모든 삭제 단계 완료. 증빙은 `docs/screenshots/`에 있습니다.

## 이번 실습 리소스 (서울 리전 ap-northeast-2)

| 리소스 | ID | 정리 결과 |
|---|---|---|
| EC2 인스턴스 | `i-03d20dd8d7eb3263a` (`mission-b61-web`) | 종료됨 (terminated) |
| Security Group | `sg-021c333abe2694a47` (`mission-b61-public-sg`) | 삭제됨 |
| Internet Gateway | `igw-016323813992e2cf6` (`mission-b61-igw`) | 분리 후 삭제됨 |
| Route Table | `rtb-061cce12216f0da91` — VPC 기본 라우팅 테이블 | VPC 삭제 시 함께 삭제됨 |
| Subnet | `subnet-0b33477b04e1f5a9f` (`mission-b61-public-subnet`) | 삭제됨 |
| VPC | `vpc-03346273d144412dd` (`mission-b61`) | 삭제됨 |
| 키 페어 | `mission-b61-key` | 삭제됨 |
| IAM 사용자/정책 | `mission-b61-user` / `MissionB61-EC2VPC-LeastPrivilege` | 유지 (요금 없음, 아래 "추가 확인" 참고) |

> 별도로 Elastic IP를 할당하지 않고 인스턴스 생성 시 자동 할당된 퍼블릭 IP(`43.201.17.39`)를 사용했으므로, EIP Release 단계는 해당 없음. 인스턴스를 종료하면 이 퍼블릭 IP는 자동으로 해제된다. (종료 후 인스턴스 목록에서 퍼블릭 IPv4 칸이 비어 있음을 확인)

## 0단계. 삭제 전 백업·증빙 확보 (문서 검토 방식 평가 대비)

> 평가는 문서 검토 방식으로 진행되므로, 리소스를 지우면 **이 서류와 스크린샷이 유일한 증빙**이 됩니다.
> 아래를 모두 체크한 뒤에만 1단계(삭제)로 넘어갑니다.

**A. 콘솔 증빙 스크린샷 (삭제 전에만 찍을 수 있음)** — `docs\screenshots\` 폴더에 저장

- [x] `evidence-vpc-map.png` — VPC 상세 화면의 "리소스 맵" (VPC·서브넷·라우팅 테이블·IGW가 한 화면에 보임, 2026-10-05 확인)
- [x] `evidence-sg-rules.png` — 보안 그룹 `mission-b61-public-sg`의 인바운드 규칙 (80, 22 두 줄, 2026-10-05 확인)
- [x] `evidence-ec2.png` — EC2 인스턴스 상세 (실행 중, 퍼블릭 IP `43.201.17.39`, t3.micro, VPC/서브넷 ID, 2026-10-05 확인)
- [x] `evidence-dashboard-before.png` — VPC 대시보드 "삭제 전" 리소스 개수 (VPC 2, 서브넷 5, 라우팅 테이블 2, IGW 2, 보안 그룹 3)
- [x] `external-access.png` — "Welcome to nginx!" 외부 접속 화면 (이미 저장됨)

**B. 서류 백업 (3중 보관)**

- [x] 1차: 로컬 `B6-1(작성중)` 폴더 (원본)
- [x] 2차: 폴더 전체를 zip(`B6-1-backup-20261005.zip`, `.pem` 제외, 14개 파일 확인)으로 만들어 **컴퓨터 밖(네이버 메일 "내게쓰기")** 과 로컬 `Documents`에 복사
- [x] 3차: 대화에서 받은 백업 zip v2(문서 + 증빙 스크린샷 사본)를 보관
- [x] 백업본을 열어 문서와 스크린샷이 들어 있고 `.pem`이 없음을 확인
- [x] **최종 재백업 (2026-10-06)** — 정리 결과가 반영된 문서·스크린샷으로 `B6-1(작성중).zip`(25개 파일, 2.79MB)을 만들어 네이버 내게쓰기로 전송(10:26). ALZip으로 열어 루트 목록에 `mission-b61-key.pem`이 없고 총 파일 수가 예상(25개)과 같음을 확인

**C. 키 파일 주의**

- [x] `mission-b61-key.pem`은 백업 zip·클라우드·GitHub에 **넣지 않음** (비밀키). 인스턴스를 삭제했으므로 이 키는 더 이상 쓸 곳이 없고, 평가 제출물에서도 제외

## 삭제 순서 (권장)

각 단계는 삭제 전 확인 창에서 대상 ID를 확인한 뒤 진행했다.

1. [x] **EC2 인스턴스 종료(Terminate)** — `i-03d20dd8d7eb3263a`. 상태가 `종료됨`으로 바뀐 것을 확인 → `evidence-ec2-terminated.png`
2. [x] **EBS 볼륨 삭제 확인** — 볼륨 목록이 "현재 이 리전에 볼륨이 없습니다" (루트 볼륨은 인스턴스와 함께 삭제됨) → `evidence-ebs-empty.png`
3. [x] **Security Group 삭제** — `sg-021c333abe2694a47` → `cleanup-sg-deleted.png`
4. [x] **Internet Gateway Detach → 삭제** — `igw-016323813992e2cf6`를 VPC에서 분리(`Detached` 확인) 후 삭제 → `cleanup-igw-detached.png`, `cleanup-igw-deleted.png`
5. [x] **Subnet 삭제** — `subnet-0b33477b04e1f5a9f` → `cleanup-subnet-deleted.png`
6. [x] **VPC 삭제** — `vpc-03346273d144412dd` (연결된 기본 라우팅 테이블 `rtb-061cce12216f0da91`도 함께 삭제됨) → 삭제 성공 알림 + 삭제 후 대시보드: `evidence-dashboard-after.png`
7. [x] **키페어 정리** — `mission-b61-key` 등록 삭제("1개의 키 페어 삭제 완료", 목록 비어 있음) → `cleanup-keypair-deleted.png`. 로컬 `mission-b61-key.pem`은 AWS에서 쓸 곳이 없는 파일이며 백업에서 제외함

## 추가 확인 (해당 시)

- [x] NAT Gateway 삭제 확인 — 이번 실습에서는 생성하지 않음(해당 없음). 삭제 후 VPC 대시보드의 NAT 게이트웨이 0
- [x] ELB/ALB 삭제 확인 — 이번 실습에서는 생성하지 않음(해당 없음)
- [x] RDS 삭제 확인 — 이번 실습에서는 생성하지 않음(해당 없음)
- [x] IAM 사용자(`mission-b61-user`)/정책(`MissionB61-EC2VPC-LeastPrivilege`) — 요금이 없는 리소스라 이번 EC2/VPC 정리 대상에서는 제외하고 **유지**함. 이후 필요 없어지면 콘솔 IAM에서 사용자 → 정책 순으로 삭제

## 최종 확인

**삭제 전후 VPC 대시보드 리소스 개수 비교** (`evidence-dashboard-before.png` ↔ `evidence-dashboard-after.png`)

| 항목 | 삭제 전 | 삭제 후 | 비고 |
|---|---|---|---|
| VPC | 2 | 1 | 남은 1개는 AWS 기본 VPC |
| 서브넷 | 5 | 4 | 기본 VPC 서브넷 4개 |
| 라우팅 테이블 | 2 | 1 | |
| 인터넷 게이트웨이 | 2 | 1 | 기본 VPC용 |
| 네트워크 ACL | 2 | 1 | |
| 보안 그룹 | 3 | 1 | 기본 VPC의 기본 보안 그룹 |
| 탄력적 IP / NAT 게이트웨이 | 0 | 0 | |

**EC2 대시보드** (`evidence-ec2-dashboard-after.png`): 인스턴스(실행 중) 0, 볼륨 0, 탄력적 IP 0, 보안 그룹 1(기본 VPC 기본값)

- 이 캡처는 키 페어를 삭제하기 직전에 찍어 **키 페어 카드가 1로 표시**됨. 키 페어 삭제는 그 직후 완료했고, 키 페어 목록 화면의 "1개의 키 페어 삭제 완료" 알림과 "표시할 키 페어 없음"(`cleanup-keypair-deleted.png`)으로 확인함. 키 페어는 요금이 발생하지 않는 리소스라 과금 확인에는 영향 없음
- 요약 카드의 숫자와 실제 목록 화면이 어긋나 보일 수 있으므로, 삭제 확인은 **목록 화면**을 기준으로 함

- [x] 과금 원인이 되는 리소스(인스턴스, 볼륨, 탄력적 IP, NAT 게이트웨이)가 모두 0개임을 위 화면들로 확인
- [x] Billing Dashboard 접속 시도 — **IAM 최소 권한 사용자에게는 결제 정보 조회가 허용되지 않아 "액세스 거부됨"** 으로 표시됨 (`cleanup-billing-denied.png`). 최소 권한이 의도대로 동작한다는 확인이기도 하며, 결제 화면 직접 확인은 대체 증빙(위 리소스 0개 화면)으로 갈음함
- [ ] (선택) 결제 데이터는 반영에 최대 24시간이 걸리므로, 원하면 1~2일 뒤 루트 계정으로 로그인해 비용이 0인지 추가 확인

| 확인자 | 확인 일시 | 비고 |
|---|---|---|
| 병우 | 2026-10-05 | 서울 리전 EC2·VPC 리소스 전부 정리, 과금 원인 리소스 0개 확인 |
| 병우 | 2026-10-06 | 최종 재백업(네이버 내게쓰기 전송, zip 25개 파일·`.pem` 제외) 확인 |
