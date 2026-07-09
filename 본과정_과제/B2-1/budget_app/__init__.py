"""budget_app — 파일 기반 콘솔 가계부.

계층 구조
--------
models      : 데이터 구조 (Transaction, Category, Budget)
repository  : 파일 I/O + 제너레이터 스트리밍 + 원자적 교체
service     : 비즈니스 로직 (검증/집계/조립)
cli         : 명령 파싱 + 대화형 입력 + 출력
decorators  : 공통 관심사 (로그/시간측정/예외처리)
errors      : 사용자 친화적 예외
"""

__version__ = "1.0.0"
