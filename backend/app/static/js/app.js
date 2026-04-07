// Shared utilities for Market Monitor

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
        document.getElementById("userEmail").textContent = data.user.email;
        return data.user;
    }
    return null;
}

async function logout() {
    await apiFetch("/api/auth/logout", { method: "POST" });
    window.location.href = "/login";
}

function formatChange(val) {
    if (val == null) return '<span class="text-muted">--</span>';
    const num = parseFloat(val);
    const cls = num >= 0 ? "text-gain" : "text-loss";
    const arrow = num >= 0 ? "bi-caret-up-fill" : "bi-caret-down-fill";
    return `<span class="${cls}"><i class="bi ${arrow}"></i> ${Math.abs(num).toFixed(2)}%</span>`;
}

function formatPrice(val) {
    if (val == null) return "--";
    return "$" + parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Ticker search
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("searchForm");
    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            const sym = document.getElementById("tickerSearch").value.trim().toUpperCase();
            if (sym) window.location.href = "/stock/" + sym;
        });
    }
});
