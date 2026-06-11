
/* ==========================================================================
   mypage.html - 유저 정보 / 크레딧 로드
   ========================================================================== */

const PLAN_LABELS = {
    free: { label: "무료 플랜", color: "bg-gray-100 text-gray-600" },
    per_use: { label: "1회권", color: "bg-blue-100 text-blue-700" },
    monthly: { label: "월정액", color: "bg-sand/30 text-camel" },
};

async function loadMyPage() {
    if (!document.getElementById("user-info")) return;

    if (!localStorage.getItem("access_token")) {
        window.location.href = "login.html";
        return;
    }

    try {
        // /mypage/me 엔드포인트 사용 (plan 포함)
        const user = await apiRequest("/mypage/me");

        const avatarEl = document.getElementById("user-avatar");
        if (avatarEl) avatarEl.textContent = (user.nickname || user.email)[0];

        const nameEl = document.getElementById("user-name");
        if (nameEl) nameEl.textContent = `${user.nickname || "사용자"} 사장님`;

        const emailEl = document.getElementById("user-email");
        if (emailEl) emailEl.textContent = user.email;

        const creditEl = document.getElementById("user-credits");
        if (creditEl) creditEl.textContent = user.credits;

        // 플랜 배지 표시
        const planEl = document.getElementById("user-plan");
        if (planEl) {
            const plan = PLAN_LABELS[user.plan] || { label: user.plan, color: "bg-gray-100 text-gray-600" };
            planEl.textContent = plan.label;
            planEl.className = `text-xs font-bold px-3 py-1 rounded-full ${plan.color}`;
        }

    } catch (e) {
        console.error("유저 정보 로드 실패", e);
    }
}

/* ==========================================================================
   mypage.html - 패키지 / 크레딧 충전
   ========================================================================== */


async function loadCreditHistory() {
    const list = document.getElementById("credits-list");
    if (!list) return;
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
        const data = await apiRequest("/mypage/credits");
        const creditEl = document.getElementById("user-credits");
        if (creditEl) creditEl.textContent = data.credits;

        const typeLabel = { earn: "충전", use: "사용", refund: "환불" };
        const tx = data.transactions || [];
        list.innerHTML = tx.length === 0
            ? `<p class="text-gray-500">사용 내역이 없습니다.</p>`
            : tx.map(t => {
                const date = new Date(t.created_at).toLocaleString('ko-KR');
                const isPlus = t.amount > 0;
                const color = isPlus ? "text-green-600" : "text-red-500";
                const sign = isPlus ? "+" : "";
                return `
                <div class="flex justify-between items-center py-2 px-3 rounded-lg hover:bg-gray-50">
                    <div>
                        <span class="font-bold text-navy">${typeLabel[t.type] || t.type}</span>
                        ${t.note ? `<span class="text-gray-500 ml-2">${t.note}</span>` : ""}
                        <p class="text-xs text-gray-400">${date}</p>
                    </div>
                    <span class="font-black ${color}">${sign}${t.amount}회</span>
                </div>`;
            }).join("");
    } catch (e) {
        console.error("크레딧 내역 로드 실패", e);
    }
}

/* ==========================================================================
   mypage.html - 비밀번호 변경
   ========================================================================== */

async function changePassword() {
    const current = document.getElementById("current-password").value;
    const next = document.getElementById("new-password").value;
    const confirm = document.getElementById("confirm-password").value;
    const msg = document.getElementById("password-message");

    const showMsg = (text, isError) => {
        msg.textContent = text;
        msg.className = `text-sm font-medium ${isError ? "text-red-500" : "text-green-600"}`;
        msg.classList.remove("hidden");
    };

    if (!current || !next || !confirm) return showMsg("모든 항목을 입력해주세요.", true);
    if (next.length < 6) return showMsg("새 비밀번호는 6자 이상이어야 합니다.", true);
    if (next !== confirm) return showMsg("새 비밀번호가 일치하지 않습니다.", true);

    try {
        const data = await apiRequest("/auth/password", {
            method: "PUT",
            body: JSON.stringify({ current_password: current, new_password: next }),
        });
        showMsg(data.message || "비밀번호가 변경되었습니다.", false);
        document.getElementById("current-password").value = "";
        document.getElementById("new-password").value = "";
        document.getElementById("confirm-password").value = "";
    } catch (e) {
        showMsg(e.message || "비밀번호 변경에 실패했습니다.", true);
    }
}

window.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("user-info")) {
        loadMyPage();
        loadCreditHistory();
        renderCreditModalPackages();
        loadHistory();
    }
});
