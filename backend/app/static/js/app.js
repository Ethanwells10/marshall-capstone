// ===== API Utilities =====

async function apiFetch(url, options = {}) {
    const defaults = { headers: { "Content-Type": "application/json" }, credentials: "same-origin" };
    const resp = await fetch(url, { ...defaults, ...options });
    if (resp.status === 401) {
        window.location.href = "/login";
        return null;
    }
    return resp;
}

async function checkAuth() {
    const resp = await fetch("/api/auth/me", { credentials: "same-origin" });
    if (resp.ok) {
        const data = await resp.json();
        document.getElementById("navLinks").style.display = "";
        document.getElementById("searchForm").style.cssText = "";
        document.getElementById("userNav").style.display = "";
        highlightActiveNav();
        return data.user;
    }
    return null;
}

async function logout() {
    await apiFetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/login";
}

// ===== Nav Highlighting =====

function highlightActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll("[data-page]").forEach(link => {
        link.classList.remove("active");
        if (path.startsWith("/" + link.dataset.page)) {
            link.classList.add("active");
        }
    });
}

// ===== Formatting =====

function formatChange(val) {
    if (val == null) return '<span class="text-neutral">--</span>';
    const num = parseFloat(val);
    const cls = num >= 0 ? "text-gain" : "text-loss";
    const bgCls = num >= 0 ? "bg-gain" : "bg-loss";
    const arrow = num >= 0 ? "bi-caret-up-fill" : "bi-caret-down-fill";
    return `<span class="${cls} ${bgCls}" style="padding:2px 6px;border-radius:4px;font-size:0.85rem;"><i class="bi ${arrow}"></i> ${Math.abs(num).toFixed(2)}%</span>`;
}

function formatPrice(val) {
    if (val == null) return "--";
    return "$" + parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function timeAgo(dateStr) {
    if (!dateStr) return "";
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return mins + "m ago";
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return hrs + "h ago";
    const days = Math.floor(hrs / 24);
    if (days < 30) return days + "d ago";
    return new Date(dateStr).toLocaleDateString();
}

// ===== Toast Notifications =====

function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    const icons = { success: "bi-check-circle-fill", error: "bi-exclamation-circle-fill", info: "bi-info-circle-fill" };
    const colors = { success: "#22c55e", error: "#ef4444", info: "#3b82f6" };

    const id = "toast-" + Date.now();
    const html = `
        <div id="${id}" class="toast show fade-in" role="alert">
            <div class="toast-body d-flex align-items-center gap-2 py-2 px-3">
                <i class="bi ${icons[type] || icons.info}" style="color:${colors[type] || colors.info};font-size:1.1rem;"></i>
                <span class="text-light">${message}</span>
            </div>
        </div>
    `;
    container.insertAdjacentHTML("beforeend", html);

    setTimeout(() => {
        const el = document.getElementById(id);
        if (el) { el.style.opacity = "0"; el.style.transition = "opacity 0.3s"; setTimeout(() => el.remove(), 300); }
    }, 3000);
}

// ===== Empty States =====

function emptyState(icon, title, message) {
    return `
        <div class="empty-state fade-in">
            <i class="bi ${icon}"></i>
            <h5>${title}</h5>
            <p>${message}</p>
        </div>
    `;
}

// ===== Skeleton Loaders =====

function skeletonCards(count = 3) {
    return Array(count).fill(`
        <div class="col-md-4">
            <div class="card"><div class="card-body">
                <div class="skeleton mb-2" style="height:14px;width:60%;"></div>
                <div class="skeleton mb-2" style="height:28px;width:80%;"></div>
                <div class="skeleton" style="height:14px;width:40%;"></div>
            </div></div>
        </div>
    `).join("");
}

// ===== Ticker Search =====

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("searchForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const sym = document.getElementById("tickerSearch").value.trim().toUpperCase();
            if (sym) window.location.href = "/search?q=" + encodeURIComponent(sym);
        });
    }
});
