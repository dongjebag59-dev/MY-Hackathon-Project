
/* ==========================================================================
   히스토리
   ========================================================================== */

async function loadHistory() {
    const list = document.getElementById("history-list");
    if (!list) return;
    const token = localStorage.getItem("access_token");
    if (!token) {
        list.innerHTML = `<p class="text-gray-500">로그인 후 이용할 수 있습니다.</p>`;
        return;
    }

    try {
        const data = await apiRequest("/history");
        const countEl = document.getElementById("history-count");
        if (countEl) countEl.textContent = `총 ${data.length}건`;

        list.innerHTML = data.length === 0
            ? `<p class="text-gray-500">생성 이력이 없습니다.</p>`
            : data.map(h => {
                const date = new Date(h.created_at).toLocaleString('ko-KR');
                return `
                <div class="p-4 rounded-xl border border-gray-200 hover:border-navy transition bg-white/50">
                    <div class="flex justify-between items-start gap-4">
                        <div class="flex-grow">
                            <p class="font-bold text-navy">${h.shop_name} <span class="text-xs text-gray-400 font-medium">· ${h.business_type}</span></p>
                            <p class="text-sm text-gray-500 mt-1">🔑 ${h.keyword} · 📍 ${h.region}</p>
                            <p class="text-xs text-gray-400 mt-1">${date} · ${h.credits_used}크레딧 사용</p>
                        </div>
                        <div class="flex gap-2 flex-shrink-0">
                            <button onclick="viewHistoryDetail(${h.id})" class="px-3 py-1.5 text-xs font-bold bg-navy text-white rounded-lg hover:bg-steel transition">상세</button>
                            <button onclick="regenerateHistory(${h.id})" class="px-3 py-1.5 text-xs font-bold bg-sand text-navy rounded-lg hover:bg-camel hover:text-white transition">재생성</button>
                            <button onclick="deleteHistory(${h.id})" class="px-3 py-1.5 text-xs font-bold bg-gray-100 text-gray-600 rounded-lg hover:bg-red-50 hover:text-red-500 transition">삭제</button>
                        </div>
                    </div>
                </div>
            `;
            }).join("");
    } catch (e) {
        console.error("히스토리 로드 실패", e);
    }
}

async function deleteHistory(id) {
    if (!confirm("이 기록을 삭제하시겠습니까?")) return;
    try {
        await apiRequest(`/history/${id}`, { method: "DELETE" });
        loadHistory();
    } catch (e) {
        alert(e.message || "삭제에 실패했습니다.");
    }
}

async function viewHistoryDetail(id) {
    try {
        const h = await apiRequest(`/history/${id}`);
        const modal = document.getElementById("history-modal");
        const title = document.getElementById("modal-title");
        const body = document.getElementById("modal-body");
        title.textContent = `${h.shop_name} - ${h.keyword}`;

        let output;
        try { output = JSON.parse(h.output_payload); } catch { output = null; }

        let text = `[가게] ${h.shop_name} (${h.business_type})\n[지역] ${h.region}\n[키워드] ${h.keyword}\n`;
        if (h.feature) text += `[특징] ${h.feature}\n`;
        text += `[톤] ${h.tone}\n\n`;

        if (output) {
            if (output.blog) {
                const b = output.blog;
                text += `📝 [블로그]\n${b.title || ""}\n\n${b.body || ""}\n\n${b.hashtags || ""}\n\n`;
            }
            if (output.review) {
                const r = output.review;
                if (r && typeof r === "object") {
                    text += `⭐ [리뷰]\n`;
                    if (r.customer_review) text += `고객 리뷰:\n${r.customer_review}\n\n`;
                    if (r.owner_reply_1) text += `답글 예시 1:\n${r.owner_reply_1}\n\n`;
                    if (r.owner_reply_2) text += `답글 예시 2:\n${r.owner_reply_2}\n\n`;
                } else {
                    text += `⭐ [리뷰]\n${r}\n\n`;
                }
            }
            if (output.shorts) {
                const s = output.shorts;
                if (s.timeline) {
                    text += `📱 [쇼츠]\n`;
                    s.timeline.forEach(cut => { text += `[${cut.time}] ${cut.caption}\n`; });
                    if (s.instagram_body) text += `\n본문: ${s.instagram_body}\n`;
                    text += "\n";
                } else {
                    text += `📱 [쇼츠]\n${s.cut1 || ""}\n${s.cut2 || ""}\n${s.cut3 || ""}\n\n`;
                }
            }
            if (output.thumbnail) {
                const thumb = output.thumbnail;
                if (thumb && typeof thumb === "object" && thumb.copies) {
                    text += `🎨 [썸네일]\n`;
                    text += `숫자형: ${thumb.copies.number_type || ""}\n`;
                    text += `질문형: ${thumb.copies.question_type || ""}\n`;
                    text += `감성형: ${thumb.copies.emotion_type || ""}\n`;
                } else {
                    const t = Array.isArray(thumb) ? thumb.join("\n") : thumb;
                    text += `🎨 [썸네일]\n${t}\n`;
                }
            }
        } else {
            text += h.output_payload;
        }

        body.textContent = text;
        modal.classList.remove("hidden");
    } catch (e) {
        alert(e.message || "상세 조회에 실패했습니다.");
    }
}

function closeHistoryDetail() {
    const modal = document.getElementById("history-modal");
    if (modal) modal.classList.add("hidden");
}

async function regenerateHistory(id) {
    if (!confirm("이 기록으로 재생성하시겠습니까? 크레딧 1회가 차감됩니다.")) return;
    try {
        const data = await apiRequest(`/history/${id}/regenerate`, { method: "POST" });
        alert("재생성이 완료되었습니다.");
        loadHistory();
        // mypage.html에서만 loadMyPage() 및 loadCreditHistory() 호출
        if (document.getElementById("user-info")) {
            loadMyPage();
            loadCreditHistory();
        }
        // generate.html 헤더 크레딧 갱신
        if (data.credits_remaining !== null && data.credits_remaining !== undefined) {
            const creditsEl = document.getElementById("header-credits");
            if (creditsEl) creditsEl.textContent = `${data.credits_remaining}회`;
        }
    } catch (e) {
        alert(e.message || "재생성에 실패했습니다.");
    }
}
