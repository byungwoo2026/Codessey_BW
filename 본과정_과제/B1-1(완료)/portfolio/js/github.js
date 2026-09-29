/* ==========================================================================
   github.js
   - GitHub API에서 저장소 목록을 가져와 Projects 섹션에 렌더링
   - 상태 → 렌더링 흐름 예시 2: API 로딩/성공/에러/빈 상태 → 화면 변경
   - 보너스: 언어별 필터링 (array.filter 활용)
   ========================================================================== */

// TODO: 아래 아이디는 메모리에 남아있던 값을 임시로 넣어둔 것입니다.
// 실제 본인 GitHub 아이디로 꼭 확인 후 수정하세요.
const GITHUB_USERNAME = "byungwoo2026";
const GITHUB_API_URL = `https://api.github.com/users/${GITHUB_USERNAME}/repos?sort=updated&per_page=9`;

const projectsGrid = document.getElementById("projects-grid");
const projectsStatus = document.getElementById("projects-status");
const projectFiltersEl = document.getElementById("project-filters");

// 현재 로드된 전체 저장소를 보관 (필터링에 재사용)
let allRepos = [];
let activeLanguage = "all";

/* -------------------- 렌더링 헬퍼 -------------------- */

const renderLoading = () => {
  projectsStatus.innerHTML = `<span class="mono">&gt; 저장소 불러오는 중<span class="cursor">_</span></span>`;
  projectsGrid.innerHTML = Array.from({ length: 3 })
    .map(() => `<div class="skeleton-card" aria-hidden="true"></div>`)
    .join("");
  projectFiltersEl.innerHTML = "";
};

const renderError = (message) => {
  projectsStatus.innerHTML = `
    <span class="status-error">⚠ ${message}</span>
    <button type="button" class="retry-btn" id="retry-fetch-btn">다시 시도</button>
  `;
  projectsGrid.innerHTML = "";
  projectFiltersEl.innerHTML = "";

  const retryBtn = document.getElementById("retry-fetch-btn");
  retryBtn.addEventListener("click", loadProjects);
};

const renderEmpty = () => {
  projectsStatus.textContent = "";
  projectsGrid.innerHTML = `<p class="mono">표시할 프로젝트가 없습니다.</p>`;
  projectFiltersEl.innerHTML = "";
};

// 구조분해 할당 + 템플릿 리터럴로 카드 HTML 생성
const buildProjectCard = ({ name, description, html_url, stargazers_count, language }) => `
  <article class="project-card">
    <h3>${name}</h3>
    <p>${description ? description : "설명이 등록되어 있지 않은 저장소입니다."}</p>
    <div class="project-meta">
      ${language ? `<span><span class="lang-dot"></span>${language}</span>` : ""}
      <span>★ ${stargazers_count}</span>
    </div>
    <a class="project-link" href="${html_url}" target="_blank" rel="noopener noreferrer">
      GitHub에서 보기 →
    </a>
  </article>
`;

const renderProjects = (repos) => {
  if (repos.length === 0) {
    projectsGrid.innerHTML = `<p class="mono">표시할 프로젝트가 없습니다.</p>`;
    return;
  }
  // map: 데이터를 HTML 카드로 변환
  projectsGrid.innerHTML = repos.map(buildProjectCard).join("");
};

/* -------------------- 보너스: 언어 필터 -------------------- */
/* 상태 → 렌더링 흐름 예시 4: 필터 버튼 클릭 → 필터 상태 변경 → 목록 변경 */

const renderFilters = (repos) => {
  const languages = repos
    .map((repo) => repo.language) // map
    .filter((language) => Boolean(language)); // filter: null 제외

  const uniqueLanguages = ["all", ...new Set(languages)];

  projectFiltersEl.innerHTML = "";

  uniqueLanguages.forEach((language) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "filter-btn" + (language === activeLanguage ? " active" : "");
    btn.textContent = language === "all" ? "전체" : language;
    btn.dataset.language = language;
    projectFiltersEl.appendChild(btn);
  });

  // 이벤트 위임 대신 forEach로 각 버튼에 직접 연결
  projectFiltersEl.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeLanguage = btn.dataset.language;

      projectFiltersEl
        .querySelectorAll(".filter-btn")
        .forEach((b) => b.classList.toggle("active", b === btn));

      const filtered =
        activeLanguage === "all"
          ? allRepos
          : allRepos.filter((repo) => repo.language === activeLanguage);

      renderProjects(filtered);
    });
  });
};

/* -------------------- 데이터 로드 -------------------- */

async function loadProjects() {
  renderLoading();

  try {
    const response = await fetch(GITHUB_API_URL);

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error("GitHub API 요청 한도를 초과했습니다 (레이트 리밋).");
      }
      if (response.status === 404) {
        throw new Error("해당 GitHub 사용자를 찾을 수 없습니다. 아이디를 확인해주세요.");
      }
      throw new Error("프로젝트를 불러올 수 없습니다.");
    }

    const repos = await response.json();

    if (!Array.isArray(repos) || repos.length === 0) {
      allRepos = [];
      renderEmpty();
      return;
    }

    allRepos = repos;
    projectsStatus.textContent = "";
    renderFilters(allRepos);
    renderProjects(allRepos);
  } catch (error) {
    renderError(error.message || "프로젝트를 불러올 수 없습니다.");
  }
}

loadProjects();
