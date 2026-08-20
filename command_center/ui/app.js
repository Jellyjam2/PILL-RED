// PILL RED Command Center Frontend Logic

let currentSession = "SESS-LIVE";

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
    document.getElementById("sessionDisplay").textContent = `SESSION: ${state.session_id}`;
    document.getElementById("valTotalObserved").textContent = state.total_observed_spins;

    // 1. Render Observation Table
    const spinsTable = document.getElementById("spinsTableBody");
    if (state.recent_spins && state.recent_spins.length > 0) {
        spinsTable.innerHTML = state.recent_spins.slice().reverse().map(s => {
            const timeStr = new Date(s.timestamp * 1000).toLocaleTimeString();
            const symbolsStr = s.outcome_symbols ? `[${s.outcome_symbols.join(", ")}]` : "N/A";
            return `
                <tr>
                    <td>#${s.spin_index}</td>
                    <td>${timeStr}</td>
                    <td class="text-cyan">${symbolsStr}</td>
                    <td>${s.payout_multiplier.toFixed(2)}x</td>
                    <td>${s.bonus_event ? '<span class="text-yellow">★ BONUS</span>' : '-'}</td>
                </tr>
            `;
        }).join("");
    } else {
        spinsTable.innerHTML = `<tr><td colspan="5" class="empty-msg">Awaiting incoming telemetry...</td></tr>`;
    }

    // 2. Render Next Locked Prediction
    if (state.pending_prediction) {
        const p = state.pending_prediction;
        const timeStr = new Date(p.timestamp_predicted * 1000).toLocaleTimeString();
        document.getElementById("valPredTarget").textContent = `TARGET: SPIN #${p.target_spin_index}`;
        document.getElementById("valPredId").textContent = p.prediction_id;
        document.getElementById("valPredDecision").textContent = `SIGNAL: ${p.decision} (${(p.confidence * 100).toFixed(0)}% Conf)`;
        document.getElementById("valPredModel").textContent = p.model_hash;
        document.getElementById("valPredTime").textContent = timeStr;
    }

    // 3. Render Resolved Predictions
    const predsTable = document.getElementById("predsTableBody");
    if (state.recent_predictions && state.recent_predictions.length > 0) {
        predsTable.innerHTML = state.recent_predictions.slice().reverse().map(p => {
            if (p.causal_status !== "VALID" || p.actual_result === null) return "";
            const statusBadge = p.is_hit 
                ? '<span class="text-green font-bold">✓ HIT</span>' 
                : '<span class="text-red font-bold">✗ MISS</span>';
            return `
                <tr>
                    <td>#${p.target_spin_index}</td>
                    <td>${p.decision}</td>
                    <td class="text-cyan">${p.actual_result}</td>
                    <td>${statusBadge}</td>
                </tr>
            `;
        }).join("");
    }

    // 4. Render Competing Models
    const modelsContainer = document.getElementById("modelsContainer");
    if (state.competing_models) {
        modelsContainer.innerHTML = state.competing_models.map(m => `
            <div class="model-card">
                <div>
                    <div class="model-name">${m.name}</div>
                    <div style="font-size: 10px; color: var(--text-muted);">${m.id}</div>
                </div>
                <div class="model-stats">
                    <div>In-Sample: ${(m.in_sample_acc * 100).toFixed(1)}%</div>
                    <div>Out-Sample: ${(m.out_sample_acc * 100).toFixed(1)}%</div>
                    <div class="elo-tag">ELO ${m.elo}</div>
                </div>
            </div>
        `).join("");
    }

    // 5. Render Scorecards & Analytics
    document.getElementById("valHitRate").textContent = `${(state.live_hit_rate * 100).toFixed(2)}%`;
    document.getElementById("valNullRate").textContent = `Null Baseline: ${(state.baseline_null_rate * 100).toFixed(2)}% (${state.hits}/${state.total_resolved_predictions} hits)`;
    
    if (state.wilson_ci_99) {
        document.getElementById("valWilsonCI").textContent = `[${(state.wilson_ci_99[0] * 100).toFixed(2)}%, ${(state.wilson_ci_99[1] * 100).toFixed(2)}%]`;
    }
    
    document.getElementById("valPValue").textContent = state.binomial_p_value < 0.0001 ? state.binomial_p_value.toExponential(4) : state.binomial_p_value.toFixed(4);
    document.getElementById("valSignificance").textContent = state.binomial_p_value < 0.01 ? "SIGNIFICANT (p < 0.01)" : "Not Significant (p >= 0.01)";
    document.getElementById("valSignificance").className = state.binomial_p_value < 0.01 ? "metric-sub text-green font-bold" : "metric-sub text-muted";

    const netEvEl = document.getElementById("valNetEV");
    netEvEl.textContent = `${(state.net_expected_value * 100).toFixed(2)}%`;
    netEvEl.className = state.net_expected_value > 0 ? "metric-value text-green" : "metric-value text-red";

    // Verdict Badge
    const badge = document.getElementById("valVerdictBadge");
    const verdictText = document.getElementById("valVerdictText");
    badge.textContent = state.audit_verdict.replace(/_/g, " ");
    verdictText.textContent = state.audit_verdict;

    if (state.audit_verdict === "REPRODUCIBLE_ECONOMIC_EDGE") {
        badge.className = "verdict-badge text-green";
    } else if (state.audit_verdict === "NULL_MODEL_CONFIRMED") {
        badge.className = "verdict-badge text-cyan";
    } else {
        badge.className = "verdict-badge text-yellow";
    }
}

// Button Events
document.getElementById("btnSimulateSpin").addEventListener("click", async () => {
    try {
        const randomSymbol = Math.floor(Math.random() * 10);
        await fetch("/api/ingest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                timestamp: Date.now() / 1000,
                game_title: "Hot Hot Fruit",
                symbols: [randomSymbol],
                payout_multiplier: randomSymbol === 7 ? 10.0 : 0.0,
                bonus_event: randomSymbol === 7
            })
        });
        fetchDashboardState();
    } catch (err) {
        console.error("Simulation failed:", err);
    }
});

document.getElementById("btnExport").addEventListener("click", () => {
    window.location.href = "/api/generate_report";
});

// Polling interval
setInterval(fetchDashboardState, 1000);
fetchDashboardState();
