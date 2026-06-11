// 토큰 관리
function saveAuth(token) {
    localStorage.setItem("access_token", token);
}

function getAccessToken() {
    return localStorage.getItem("access_token");
}

function clearAuth() {
    localStorage.removeItem("access_token");
}

function requireAuth() {
    if (!getAccessToken()) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

// 메시지 표시
function setMessage(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.style.color = isError ? "#e53e3e" : "#2563eb";
}

// 로그인 (onclick="login()" 핸들러)
async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        setMessage("message", "이메일과 비밀번호를 입력해주세요.", true);
        return;
    }

    try {
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "로그인에 실패했습니다.");
        saveAuth(data.access_token);
        window.location.href = "generate.html";
    } catch (error) {
        setMessage("message", error.message || "로그인에 실패했습니다.", true);
    }
}

// 회원가입 (onclick="register()" 핸들러)
async function register() {
    const email = document.getElementById("email").value.trim();
    const nickname = document.getElementById("nickname").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !nickname || !password) {
        setMessage("message", "모든 항목을 입력해주세요.", true);
        return;
    }

    try {
        await apiRequest("/auth/signup", {
            method: "POST",
            body: JSON.stringify({ email, nickname, password }),
        });
        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });
        const loginData = await res.json();
        if (!res.ok) throw new Error(loginData.detail || "로그인에 실패했습니다.");
        saveAuth(loginData.access_token);
        window.location.href = "generate.html";
    } catch (error) {
        setMessage("message", error.message || "회원가입에 실패했습니다.", true);
    }
}

// 로그아웃은 my_script.js의 logout() 함수에서 처리합니다.

// 네비게이션 로그인 상태 반영
function initAuthNav() {
    const isLoggedIn = !!getAccessToken();

    // 로그인/회원가입 링크 (비로그인 전용)
    const loginLink = document.getElementById("nav-login");
    const registerLink = document.getElementById("nav-register");
    // 로그인 후 메뉴 (로그인 전용)
    const logoutBtn = document.getElementById("nav-logout");
    const mypageLink = document.getElementById("nav-mypage");
    const mypageLink2 = document.getElementById("nav-mypage2");

    const ctaGuest = document.getElementById("cta-guest");

    if (isLoggedIn) {
        if (loginLink) loginLink.classList.add("hidden");
        if (registerLink) registerLink.classList.add("hidden");
        if (logoutBtn) logoutBtn.classList.remove("hidden");
        if (mypageLink) mypageLink.classList.remove("hidden");
        if (mypageLink2) mypageLink2.classList.remove("hidden");
        if (ctaGuest) ctaGuest.classList.add("hidden");
    } else {
        if (loginLink) loginLink.classList.remove("hidden");
        if (registerLink) registerLink.classList.remove("hidden");
        if (logoutBtn) logoutBtn.classList.add("hidden");
        if (mypageLink) mypageLink.classList.add("hidden");
        if (mypageLink2) mypageLink2.classList.add("hidden");
        if (ctaGuest) ctaGuest.classList.remove("hidden");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initAuthNav();

    const logoutBtn = document.getElementById("nav-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", logout);
    }
});
