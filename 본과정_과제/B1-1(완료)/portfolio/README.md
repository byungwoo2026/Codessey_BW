# 병우 | Developer Portfolio

Python 기반 AI 개발자 병우를 소개하는 반응형 개인 포트폴리오 웹사이트입니다.
외부 라이브러리/프레임워크 없이 순수 HTML, CSS, JavaScript만으로 제작했습니다.

## 배포 URL

- (배포 후 이 자리에 GitHub Pages 링크를 채워주세요) `https://<GitHub아이디>.github.io/<저장소이름>/`

## 사용 기술

- HTML5 (시맨틱 마크업)
- CSS3 (CSS 변수, Flexbox, Grid, 미디어 쿼리)
- Vanilla JavaScript (ES6+, Fetch API, IntersectionObserver)
- GitHub REST API (저장소 목록 연동)
- 폰트: Google Fonts (Space Grotesk, Inter, JetBrains Mono)

## 폴더 구조

```
portfolio/
├─ index.html
├─ css/
│  └─ style.css
├─ js/
│  ├─ main.js      # 테마 토글, 헤더 스크롤, 햄버거 메뉴, 스무스 스크롤, 스크롤 애니메이션
│  ├─ github.js    # GitHub API 연동 + 언어 필터(보너스)
│  └─ form.js      # 문의 폼 유효성 검사
├─ images/
│  └─ avatar.svg   # 프로필 이미지 placeholder (실제 사진으로 교체 필요)
└─ README.md
```

## 반드시 확인/수정해야 하는 부분

1. **GitHub 아이디** — `js/github.js` 상단의 `GITHUB_USERNAME` 값을 본인의 실제 GitHub 아이디로 확인/수정하세요.
2. **프로필 이미지** — `images/avatar.svg`를 실제 프로필 사진(jpg/png)으로 교체하고, `index.html`의 `<img src="images/avatar.svg">` 경로를 맞춰 수정하세요.
3. **자기소개 / 기술 스택 문구** — `index.html`의 About, Skills 섹션 내용을 본인 실제 정보로 수정하세요.
4. **소셜 링크** — Footer의 GitHub / LinkedIn 링크(`href`)를 실제 주소로 수정하세요.

## 구현된 기준값 (요구사항 명시 사항)

- 스크롤 탑 버튼 노출 기준: `scrollY > 300px` (`js/main.js`의 `SCROLL_TOP_THRESHOLD`)
- 네비게이션 배경색 변경 기준: `scrollY > 60px` (`js/main.js`의 `SCROLL_HEADER_THRESHOLD`)
- 스크롤 애니메이션 IntersectionObserver threshold: `0.2` (`js/main.js`의 `REVEAL_THRESHOLD`)

## 구현된 보너스 과제

- 시스템 다크 모드 감지 (`prefers-color-scheme`) — localStorage에 저장된 값이 없을 때 시스템 설정을 기본값으로 사용
- GitHub 프로젝트 언어별 필터링 (`array.filter` 활용)

## 로컬 개발 환경

1. VS Code에서 이 폴더를 엽니다.
2. `Live Server` 확장을 설치합니다.
3. `index.html`을 우클릭 → `Open with Live Server`로 실행합니다.

## 배포 방법 (GitHub Pages)

1. GitHub에 새 저장소를 생성합니다.
2. 이 폴더의 내용을 저장소에 push 합니다.
3. 저장소 `Settings → Pages`에서 배포 브랜치(main)와 폴더(`/root`)를 지정합니다.
4. 몇 분 후 발급되는 URL로 접속해 정상 동작을 확인합니다.

## 스크린샷

- (데스크톱/모바일/다크모드 스크린샷을 촬영해 이 자리에 추가하세요)
