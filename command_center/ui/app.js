// PILL RED Modern Multi-Page Dashboard Logic

let currentSession = "SESS-LIVE";

// 1. Page Switching Logic
function switchPage(pageId) {
    document.querySelectorAll(".nav-tab").forEach(tab => {
        if (tab.dataset.page === pageId) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });

    document.querySelectorAll(".page-view").forEach(page => {
        if (page.id === `page-${pageId}`) {
            page.classList.add("active");
        } else {
            page.classList.remove("active");
        }
    });
}

// Attach tab click listeners
document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
        switchPage(tab.dataset.page);
    });
});

function getModelPill(status) {
    switch (status) {
        case "VERIFIED": return { class: "pill-verified", text: "VERIFIED" };
        case "MONITORED": return { class: "pill-monitored", text: "MONITORED" };
        case "DEGRADED": return { class: "pill-degraded", text: "DEGRADED" };
        case "REVOKED": return { class: "pill-degraded", text: "REVOKED" };
        case "CANDIDATE": return { class: "pill-cyan", text: "CANDIDATE" };
        case "BENCHMARK": return { class: "pill-benchmark", text: "BENCHMARK" };
        default: return { class: "pill-benchmark", text: status || "CANDIDATE" };
    }
}

// 2. Fetch & Render State
async function fetchDashboardState() {
    try {
        const res = await fetch("/api/state");
        if (!res.ok) return;
        const state = await res.json();
        renderDashboard(state);
    } catch (err) {
        console.error("Failed to fetch state:", err);
    }
}

function renderDashboard(state) {
    currentSession = state.session_id;
    document.getElementById("valTotalObserved").textContent = state.total_observed_spins;

    // --- Page 1: Overview ---
    // Hero Pre-Commitment
    if (state.pending_prediction) {
        const p = state.pending_prediction;
        const timeStr = new Date(p.timestamp_predicted * 1000).toLocaleTimeString();
        document.getElementById("valHeroTarget").textContent = `TARGET: EVENT #${p.target_spin_index}`;
        document.getElementById("valHeroSignal").textContent = `SIGNAL: ${p.decision} (${(p.confidence * 100).toFixed(0)}% Conf)`;
        document.getElementById("valHeroPredId").textContent = p.prediction_id;
        document.getElementById("valHeroModel").textContent = p.model_hash;
        document.getElementById("valHeroTime").textContent = timeStr;
    }

    // KPI Metrics
    document.getElementById("valHitRate").textContent = `${(state.live_hit_rate * 100).toFixed(2)}%`;
    const ciText = state.wilson_ci_99 ? `[${(state.wilson_ci_99[0] * 100).toFixed(1)}%, ${(state.wilson_ci_99[1] * 100).toFixed(1)}%]` : `[0.0%, 0.0%]`;
    document.getElementById("valNullRate").textContent = `Null: 10% (${state.hits}/${state.total_resolved_predictions} hits) | 99% CI: ${ciText}`;

    // Realized Betting P/L
    const pnlVal = state.realized_pnl_zar || 0.0;
    const pnlEl = document.getElementById("valRealizedPnl");
    pnlEl.textContent = `${pnlVal >= 0 ? '+' : ''}R${pnlVal.toFixed(2)}`;
    pnlEl.className = pnlVal >= 0 ? "kpi-value text-green" : "kpi-value text-red";
    document.getElementById("valActiveWagerCount").textContent = `${state.active_wager_count || 0} Active Wagers placed`;

    // Capital Preserved / Avoided Loss
    const avoidedVal = state.avoided_loss_zar || 0.0;
    document.getElementById("valAvoidedLoss").textContent = `R${avoidedVal.toFixed(2)}`;
    document.getElementById("valAvoidedLossCount").textContent = `${state.avoided_loss_count || 0} Dry streaks avoided`;

    // Overview Models Table
    const overviewModelsBody = document.getElementById("overviewModelsBody");
    if (state.competing_models) {
        overviewModelsBody.innerHTML = state.competing_models.map(m => {
            const pill = getModelPill(m.status);
            return `
                <tr>
                    <td><strong>${m.name}</strong></td>
                    <td><code>${m.id}</code></td>
                    <td>${(m.in_sample_acc * 100).toFixed(1)}%</td>
                    <td>${(m.out_sample_acc * 100).toFixed(1)}%</td>
                    <td><strong class="text-yellow">ELO ${m.elo}</strong></td>
                    <td><span class="status-pill ${pill.class}">${pill.text}</span></td>
                </tr>
            `;
        }).join("");
    }

    // --- Page 2: Live Stream ---
    const spinsTable = document.getElementById("spinsTableBody");
    if (state.recent_spins && state.recent_spins.length > 0) {
        spinsTable.innerHTML = state.recent_spins.slice().reverse().map(s => {
            const timeStr = new Date(s.timestamp * 1000).toLocaleTimeString();
            const symbolsStr = s.outcome_symbols ? `[${s.outcome_symbols.join(", ")}]` : "N/A";
            return `
                <tr>
                    <td><strong>#${s.spin_index}</strong></td>
                    <td>${timeStr}</td>
                    <td class="text-cyan">${symbolsStr}</td>
                    <td>${s.payout_multiplier.toFixed(2)}x</td>
                    <td>${s.bonus_event ? '<span class="text-yellow">★ BONUS</span>' : '-'}</td>
                    <td><button class="delete-btn" onclick="deleteSpin(${s.spin_index})" title="Delete event #${s.spin_index}">🗑️</button></td>
                </tr>
            `;
        }).join("");
    } else {
        spinsTable.innerHTML = `<tr><td colspan="6" class="empty-msg">Awaiting incoming telemetry...</td></tr>`;
    }

    // --- Page 3: Model Arena ---
    const modelsGrid = document.getElementById("modelsGridContainer");
    if (state.competing_models) {
        modelsGrid.innerHTML = state.competing_models.map(m => {
            const pill = getModelPill(m.status);
            return `
                <div class="model-row-card">
                    <div class="model-row-left">
                        <span class="status-pill ${pill.class}">${pill.text}</span>
                        <div>
                            <div class="model-title">${m.name}</div>
                            <div class="model-id-tag">${m.id} // HASH-${m.id.slice(-4)}</div>
                        </div>
                    </div>
                    <div class="model-row-stats">
                        <div>In-Sample: <strong>${(m.in_sample_acc * 100).toFixed(1)}%</strong></div>
                        <div>Out-Sample: <strong>${(m.out_sample_acc * 100).toFixed(1)}%</strong></div>
                        <div class="text-yellow"><strong>ELO ${m.elo}</strong></div>
                    </div>
                </div>
            `;
        }).join("");
    }

    // --- Page 4: Forensic Ledger ---
    const predsTable = document.getElementById("predsTableBody");
    const validResolved = state.recent_predictions 
        ? state.recent_predictions.filter(p => p.causal_status === "VALID" && p.actual_result !== null)
        : [];

    if (validResolved.length > 0) {
        predsTable.innerHTML = validResolved.slice().reverse().map(p => {
            const statusBadge = p.is_hit 
                ? '<span class="text-green font-bold">✓ HIT</span>' 
                : '<span class="text-red font-bold">✗ MISS</span>';
            return `
                <tr>
                    <td><strong>EVENT #${p.target_spin_index}</strong></td>
                    <td>SIGNAL: ${p.decision}</td>
                    <td class="text-cyan">${p.actual_result}</td>
                    <td>${statusBadge} (<span class="text-green">VALID_MERKLE_SEALED</span>)</td>
                </tr>
            `;
        }).join("");
    } else {
        predsTable.innerHTML = `<tr><td colspan="4" class="empty-msg">No resolved predictions yet.</td></tr>`;
    }
}

async function quickLogOutcome(symbol, payout = 0.0, isBonus = false) {
    try {
        await fetch("/api/ingest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                timestamp: Date.now() / 1000,
                game_title: "Hot Hot Fruit",
                symbols: [symbol],
                payout_multiplier: payout,
                bonus_event: isBonus
            })
        });
        fetchDashboardState();
    } catch (err) {
        console.error("Outcome logging error:", err);
    }
}

function triggerExport() {
    window.location.href = "/api/generate_report";
}

const btnExportTop = document.getElementById("btnExportTop");
if (btnExportTop) btnExportTop.addEventListener("click", triggerExport);

const btnExportLedger = document.getElementById("btnExportLedger");
if (btnExportLedger) btnExportLedger.addEventListener("click", triggerExport);

// Browser Launcher
const btnLaunchBrowser = document.getElementById("btnLaunchBrowser");
if (btnLaunchBrowser) {
    btnLaunchBrowser.addEventListener("click", async () => {
        const url = document.getElementById("inputGameUrl").value;
        btnLaunchBrowser.disabled = true;
        btnLaunchBrowser.textContent = "Connecting...";
        try {
            const res = await fetch("/api/browser/launch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url })
            });
            const data = await res.json();
            updateBrowserStatus(data.status);
        } catch (err) {
            console.error("Browser launch error:", err);
            updateBrowserStatus("ERROR");
        } finally {
            btnLaunchBrowser.disabled = false;
            btnLaunchBrowser.textContent = "🚀 Launch Game Window";
        }
    });
}

function updateBrowserStatus(status) {
    const badge = document.getElementById("browserStatusBadge");
    if (!badge) return;
    badge.textContent = status;
    if (status === "ATTACHED_AND_OBSERVING") {
        badge.className = "status-pill pill-verified";
    } else if (status === "LAUNCHING") {
        badge.className = "status-pill pill-monitored";
    } else if (status === "ERROR") {
        badge.className = "status-pill pill-degraded";
    } else {
        badge.className = "status-pill pill-benchmark";
    }
}

async function pollBrowserStatus() {
    try {
        const res = await fetch("/api/browser/status");
        if (res.ok) {
            const data = await res.json();
            updateBrowserStatus(data.status);
        }
    } catch (e) {}
}

// Delete and Undo Handlers
async function deleteSpin(spinIndex) {
    if (confirm(`Delete Event #${spinIndex} from the telemetry feed?`)) {
        try {
            const res = await fetch("/api/telemetry/delete", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ spin_index: spinIndex })
            });
            if (res.ok) fetchDashboardState();
        } catch (err) {
            console.error("Delete spin error:", err);
        }
    }
}

async function undoLastSpin() {
    try {
        const res = await fetch("/api/telemetry/undo", { method: "POST" });
        if (res.ok) fetchDashboardState();
    } catch (err) {
        console.error("Undo spin error:", err);
    }
}

const btnUndoLast = document.getElementById("btnUndoLast");
if (btnUndoLast) btnUndoLast.addEventListener("click", undoLastSpin);

// Session Reset Handlers
async function handleSessionReset() {
    if (confirm("Reset current audit session and start a fresh Genesis block?")) {
        try {
            const res = await fetch("/api/reset", { method: "POST" });
            if (res.ok) {
                fetchDashboardState();
            }
        } catch (err) {
            console.error("Session reset error:", err);
        }
    }
}

const btnResetTop = document.getElementById("btnResetSession");
if (btnResetTop) btnResetTop.addEventListener("click", handleSessionReset);

const btnResetSettings = document.getElementById("btnResetSettings");
if (btnResetSettings) btnResetSettings.addEventListener("click", handleSessionReset);

// Polling interval
setInterval(fetchDashboardState, 1000);
setInterval(pollBrowserStatus, 2000);
fetchDashboardState();
pollBrowserStatus();
