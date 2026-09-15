/* ==========================================================================
   form.js
   - Contact 폼 유효성 검사
   - 상태 → 렌더링 흐름 예시 3: 폼 입력 → 유효성 상태 변경 → 에러 메시지 표시/숨김
   ========================================================================== */

const contactForm = document.getElementById("contact-form");
const successMessageEl = document.getElementById("form-success-message");

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const fieldConfigs = [
  {
    input: document.getElementById("name"),
    errorEl: document.getElementById("name-error"),
    validate: (value) => (value.trim().length === 0 ? "이름을 입력해주세요." : ""),
  },
  {
    input: document.getElementById("email"),
    errorEl: document.getElementById("email-error"),
    validate: (value) => {
      if (value.trim().length === 0) return "이메일을 입력해주세요.";
      if (!EMAIL_PATTERN.test(value.trim())) return "이메일 형식이 올바르지 않습니다.";
      return "";
    },
  },
  {
    input: document.getElementById("message"),
    errorEl: document.getElementById("message-error"),
    validate: (value) => (value.trim().length === 0 ? "메시지를 입력해주세요." : ""),
  },
];

const setFieldError = ({ input, errorEl }, message) => {
  errorEl.textContent = message;
  input.closest(".form-field").classList.toggle("has-error", Boolean(message));
};

// 입력 중(input 이벤트) 실시간으로 에러 상태 갱신
fieldConfigs.forEach((field) => {
  field.input.addEventListener("input", () => {
    const message = field.validate(field.input.value);
    setFieldError(field, message);
  });
});

contactForm.addEventListener("submit", (event) => {
  event.preventDefault();
  successMessageEl.textContent = "";

  // 구조분해 + map으로 전체 필드를 검증하고, 에러 메시지 배열을 만든 뒤 filter로 실패 항목만 추림
  const validationResults = fieldConfigs.map((field) => ({
    field,
    message: field.validate(field.input.value),
  }));

  validationResults.forEach(({ field, message }) => setFieldError(field, message));

  const hasError = validationResults.filter(({ message }) => message).length > 0;

  if (hasError) {
    const firstInvalid = validationResults.find(({ message }) => message);
    if (firstInvalid) firstInvalid.field.input.focus();
    return;
  }

  // 실제 전송 서버가 없으므로, 성공 상태만 화면에 표시하고 폼을 초기화한다.
  successMessageEl.textContent = "메시지가 성공적으로 전송되었습니다. 감사합니다!";
  contactForm.reset();
  fieldConfigs.forEach((field) => setFieldError(field, ""));
});
