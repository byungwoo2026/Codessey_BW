/* ==========================================================================
   main.js
   - 다크 모드 토글 (localStorage 유지, 시스템 설정 감지 보너스 포함)
   - 헤더 스크롤 스타일 변경
   - 햄버거 메뉴 토글
   - 네비게이션 부드러운 스크롤
   - 스크롤 탑 버튼
   - IntersectionObserver 기반 스크롤 등장 애니메이션
   ========================================================================== */

/* -------------------- 1. 다크 모드 -------------------- */
/* 상태 → 렌더링 흐름 예시 1: 테마 상태 변경 → 전체 화면 스타일 변경 */

const THEME_STORAGE_KEY = "portfolio-theme";
const rootEl = document.documentElement;
const themeToggleBtn = document.getElementById("theme-toggle");
const themeToggleIcon = themeToggleBtn
  ? themeToggleBtn.querySelector(".theme-toggle-icon")
  : null;
const statusThemeEl = document.getElementById("status-theme");

const getPreferredTheme = () => {
  const saved = localStorage.getItem(THEME_STORAGE_KEY);
  if (saved === "light" || saved === "dark") {
    return saved;
  }
  // 보너스: 저장된 값이 없으면 시스템 다크모드 설정 감지
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  return prefersDark ? "dark" : "light";
};

const applyTheme = (theme) => {
  if (theme === "dark") {
    rootEl.setAttribute("data-theme", "dark");
    if (themeToggleIcon) themeToggleIcon.textContent = "☀️";
    if (themeToggleBtn) themeToggleBtn.setAttribute("aria-pressed", "true");
  } else {
    rootEl.removeAttribute("data-theme");
    if (themeToggleIcon) themeToggleIcon.textContent = "🌙";
    if (themeToggleBtn) themeToggleBtn.setAttribute("aria-pressed", "false");
  }
  if (statusThemeEl) {
    statusThemeEl.textContent = `THEME: ${theme.toUpperCase()}`;
  }
};

let currentTheme = getPreferredTheme();
applyTheme(currentTheme);

if (themeToggleBtn) {
  themeToggleBtn.addEventListener("click", () => {
    currentTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(currentTheme);
    localStorage.setItem(THEME_STORAGE_KEY, currentTheme);
  });
}

/* -------------------- 2. 헤더 스크롤 스타일 -------------------- */

const siteHeader = document.getElementById("site-header");
const SCROLL_HEADER_THRESHOLD = 60; // 기준값: 60px (README에도 명시)

const handleHeaderScroll = () => {
  if (window.scrollY > SCROLL_HEADER_THRESHOLD) {
    siteHeader.classList.add("is-scrolled");
  } else {
    siteHeader.classList.remove("is-scrolled");
  }
};

window.addEventListener("scroll", handleHeaderScroll);
handleHeaderScroll();

/* -------------------- 3. 햄버거 메뉴 -------------------- */

const hamburgerBtn = document.getElementById("hamburger-btn");
const navMenu = document.getElementById("nav-menu");

const closeMenu = () => {
  hamburgerBtn.classList.remove("active");
  navMenu.classList.remove("active");
  hamburgerBtn.setAttribute("aria-expanded", "false");
};

hamburgerBtn.addEventListener("click", () => {
  const isActive = navMenu.classList.toggle("active");
  hamburgerBtn.classList.toggle("active", isActive);
  hamburgerBtn.setAttribute("aria-expanded", String(isActive));
});

/* -------------------- 4. 네비게이션 부드러운 스크롤 -------------------- */

const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    const targetId = link.getAttribute("href");
    const targetEl = document.querySelector(targetId);
    if (!targetEl) return;

    event.preventDefault();
    targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
    closeMenu();
  });
});

/* -------------------- 5. 스크롤 탑 버튼 -------------------- */

const scrollTopBtn = document.getElementById("scroll-top-btn");
const SCROLL_TOP_THRESHOLD = 300; // 기준값: 300px (README에도 명시)

const handleScrollTopButton = () => {
  if (window.scrollY > SCROLL_TOP_THRESHOLD) {
    scrollTopBtn.classList.add("is-visible");
  } else {
    scrollTopBtn.classList.remove("is-visible");
  }
};

window.addEventListener("scroll", handleScrollTopButton);
handleScrollTopButton();

scrollTopBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});

/* -------------------- 6. 스크롤 등장 애니메이션 -------------------- */

const revealTargets = document.querySelectorAll(".reveal");
const REVEAL_THRESHOLD = 0.2; // 기준값: 0.2 (README에도 명시)

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: REVEAL_THRESHOLD }
  );

  revealTargets.forEach((target) => revealObserver.observe(target));
} else {
  // IntersectionObserver 미지원 브라우저 대비: 즉시 노출
  revealTargets.forEach((target) => target.classList.add("is-visible"));
}
