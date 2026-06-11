
/* ==========================================================================
   크레딧 소진 모달
   ========================================================================== */

async function showCreditModal(message) {
    const modal = document.getElementById("credit-modal");
    if (!modal) return;

    const msgEl = document.getElementById("credit-modal-msg");
    if (msgEl) msgEl.textContent = message;

    modal.classList.remove("hidden");

    // 패키지 목록을 API에서 불러와 렌더링
    await renderCreditModalPackages();
}

function closeCreditModal() {
    const modal = document.getElementById("credit-modal");
    if (modal) modal.classList.add("hidden");
}

async function renderCreditModalPackages() {
    const container = document.getElementById("credit-modal-packages");
    if (!container) return;

    try {
        const packages = await apiRequest("/mypage/packages");
        const labels  = { light: "라이트", basic: "베이직", pro: "프로" };
        const badges  = { light: "", basic: "🔥 인기", pro: "💎 베스트" };
        const colors  = {
            light: "border-gray-200 hover:border-navy",
            basic: "border-sand hover:border-camel",
            pro  : "border-navy hover:border-steel bg-navy/5",
        };

        container.innerHTML = packages.map(pkg => `
            <div class="relative border-2 ${colors[pkg.id] || 'border-gray-200 hover:border-navy'} rounded-2xl p-4 text-center transition cursor-pointer group"
                 onclick="chargeCreditsFromModal('${pkg.id}')">
                ${badges[pkg.id] ? `<span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-camel text-white text-xs font-bold px-2.5 py-0.5 rounded-full whitespace-nowrap">${badges[pkg.id]}</span>` : ""}
                <p class="font-black text-sm text-navy mb-1 mt-1">${labels[pkg.id] || pkg.id}</p>
                <p class="text-2xl font-black text-navy">${pkg.credits}<span class="text-xs font-bold text-gray-500">회</span></p>
                <p class="text-camel font-black text-sm mb-3">${pkg.price.toLocaleString()}원</p>
                <button class="w-full bg-navy text-white font-bold py-2 rounded-xl group-hover:bg-steel transition text-xs">충전하기</button>
            </div>
        `).join("");
    } catch (e) {
        container.innerHTML = `<p class="col-span-3 text-center text-red-400 text-sm">패키지를 불러오지 못했습니다.</p>`;
    }
}

async function chargeCreditsFromModal(packageId) {
    const packageLabels = { light: "라이트", basic: "베이직", pro: "프로" };
    const label = packageLabels[packageId] || packageId;
    if (!confirm(`'${label}' 패키지로 충전하시겠습니까?\n(실제 결제 없이 테스트 충전됩니다)`)) return;

    try {
        const data = await apiRequest("/mypage/charge", {
            method: "POST",
            body: JSON.stringify({ package: packageId }),
        });

        closeCreditModal();
        alert(`✅ ${data.charged}크레딧이 충전되었습니다!\n현재 잔여 크레딧: ${data.credits}회`);

        // 헤더 크레딧 즉시 갱신
        const creditsEl = document.getElementById("header-credits");
        if (creditsEl) creditsEl.textContent = `${data.credits}회`;

        // mypage.html이라면 내역도 갱신
        const creditEl = document.getElementById("user-credits");
        if (creditEl) creditEl.textContent = data.credits;
        if (document.getElementById("credits-list")) loadCreditHistory();
    } catch (e) {
        alert(e.message || "충전에 실패했습니다.");
    }
}

/* ==========================================================================
   mypage.html - 로그아웃
   ========================================================================== */

function logout() {
    if (confirm("로그아웃 하시겠습니까?")) {
        localStorage.removeItem("access_token");
        window.location.href = "index.html";
    }
}

/* ==========================================================================
   페이지 공통 - 헤더 크레딧 표시
   ========================================================================== */

async function loadCreditsDisplay() {
    const el = document.getElementById("header-credits");
    if (!el) return;
    const token = localStorage.getItem("access_token");
    if (!token) return;
    try {
        const user = await apiRequest("/auth/me");
        el.textContent = `${user.credits}회`;
    } catch (e) {}
}

window.addEventListener("DOMContentLoaded", () => {
    loadCreditsDisplay();
});
