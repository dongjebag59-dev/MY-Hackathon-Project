/* ==========================================================================
   토스트 알림 시스템 (window.alert 교체)
   ========================================================================== */

function showToast(message, type) {
    // 컨테이너 생성 (없으면)
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    // 타입 자동 감지
    if (!type) {
        const m = message || "";
        if (/✅|완료|충전|변경|성공|저장/.test(m))   type = "success";
        else if (/❌|실패|오류|에러|없습니다|잘못/.test(m)) type = "error";
        else if (/⚠|경고|만료|종료|소진/.test(m))   type = "warning";
        else                                           type = "info";
    }

    const icons = { success: "✅", error: "❌", warning: "⚠️", info: "💬" };
    const titles = { success: "완료", error: "오류", warning: "주의", info: "알림" };
    const duration = type === "error" ? 4500 : 3500;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.style.position = "relative";
    toast.style.overflow = "hidden";
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <div class="toast-body">
            <div class="toast-title">${titles[type]}</div>
            <div class="toast-msg">${message}</div>
        </div>
        <div class="toast-progress" style="animation-duration: ${duration}ms;"></div>
    `;

    // 클릭 시 즉시 닫기
    toast.addEventListener("click", () => removeToast(toast));
    container.appendChild(toast);

    // 자동 제거
    setTimeout(() => removeToast(toast), duration);
}

function removeToast(toast) {
    if (toast.classList.contains("hiding")) return;
    toast.classList.add("hiding");
    toast.addEventListener("animationend", () => toast.remove(), { once: true });
}

// 기존 alert() 전부 토스트로 교체 (confirm은 유지)
window._nativeAlert = window.alert;
window.alert = (msg) => showToast(String(msg));

const API_BASE = "/api";

async function apiRequest(path, options = {}) {
    const token = localStorage.getItem("access_token");

    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(options.headers || {}),
        },
        ...options,
    });

    if (response.status === 204) {
        return null;
    }

    if (response.status === 401) {
        localStorage.removeItem("access_token");
        if (path !== "/auth/login") {
            window.location.href = "login.html";
            return new Promise(() => {});
        }
    }

    const contentType = response.headers.get("content-type") || "";
    const rawText = await response.text();
    const payload = contentType.includes("application/json") && rawText
        ? JSON.parse(rawText)
        : rawText;

    if (!response.ok) {
        let detail = typeof payload === "object" && payload !== null
            ? payload.detail
            : payload;
        if (Array.isArray(detail)) {
            detail = detail.map(e => e.msg || e).join(", ");
        }
        const err = new Error(detail || "요청 처리 중 오류가 발생했습니다.");
        err.status = response.status;
        err.payload = payload;
        throw err;
    }

    return payload;
}
