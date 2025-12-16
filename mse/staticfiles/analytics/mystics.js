/******************************************************************************
 * MYSTICS ANALYTICS — UNIFIED FRONTEND JS (Roster + Player + Dashboard + Stats)
 * This script autodetects page type and initializes ONLY what is needed.
 ******************************************************************************/

/* ----------------------------- GLOBAL HELPERS ----------------------------- */

function $(selector) {
    return document.querySelector(selector);
}
function $all(selector) {
    return document.querySelectorAll(selector);
}

async function getJSON(url) {
    try {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error("API error " + resp.status);
        return await resp.json();
    } catch (err) {
        console.error("❌ Fetch failed:", err);
        return null;
    }
}

function destroyIfExists(chart) {
    if (chart) chart.destroy();
}

/* ----------------------------- PAGE DETECTORS ----------------------------- */

const isRosterPage = !!$("#playerSelect") && !!$("#playerDetail");
const isPlayerDetailPage = !!$("#playerDetail") && !!$("#playerTrendChart") && !isRosterPage;
const isTeamDashboard = !!$("#teamDashboard");
const isLeagueDashboard = document.body.innerHTML.includes("League-Wide Analytics");
const isStatsPage = !!$("#demoCharts");

/* ========================================================================== */
/*                            ROSTER PAGE LOGIC                               */
/* ========================================================================== */

let rosterTrendChart = null;

function initRosterPage() {
    console.log("🎯 Initializing Roster Page");

    const select = $("#playerSelect");
    const detail = $("#playerDetail");
    const players = JSON.parse(detail.dataset.players);

    const chartUrlTemplate = select.dataset.playerChartUrl; // /analytics/api/player/0/game-log/

    function updateBio(player) {
        $("#playerName").textContent = player.name;
        $("#playerJersey").textContent = "#" + (player.jersey || "--");
        $("#playerAge").textContent = player.age || "-";
        $("#playerHeight").textContent = player.height || "-";
        $("#playerWeight").textContent = player.weight || "-";

        $("#playerPhoto").src =
            player.headshot && player.headshot.trim() !== ""
                ? player.headshot
                : "/static/analytics/images/default-player.jpg";
    }

    async function updateChart(playerId) {
        const url = chartUrlTemplate.replace("0", playerId);
        const data = await getJSON(url);
        if (!data) return;

        const labels = data.map(g => g.game.date);
        const points = data.map(g => g.pts);

        destroyIfExists(rosterTrendChart);

        const ctx = $("#playerTrendChart");
        rosterTrendChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Points",
                        data: points,
                        borderWidth: 2,
                        borderColor: "rgba(220, 20, 60, 0.9)",
                        backgroundColor: "rgba(220, 20, 60, 0.3)",
                        tension: 0.3,
                    },
                ],
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } },
        });
    }

    select.addEventListener("change", () => {
        const p = players.find(x => x.id == select.value);
        updateBio(p);
        updateChart(p.id);
    });

    // Auto-load first player
    const first = players[0];
    updateBio(first);
    updateChart(first.id);
}

/* ========================================================================== */
/*                          PLAYER DETAIL PAGE LOGIC                          */
/* ========================================================================== */

let playerDetailChart = null;

function initPlayerDetailPage() {
    console.log("🎯 Initializing Player Detail Page");

    const select = $("#playerSelect");
    const chartUrl = select.dataset.playerChartUrl;

    async function loadPlayerTrend() {
        const data = await getJSON(chartUrl);
        if (!data) return;

        const labels = data.map(g => g.game.date);
        const pts = data.map(g => g.pts);

        destroyIfExists(playerDetailChart);

        const ctx = $("#playerTrendChart");
        playerDetailChart = new Chart(ctx, {
            type: "line",
            data: {
                labels,
                datasets: [
                    {
                        label: "Points",
                        data: pts,
                        borderColor: "crimson",
                        backgroundColor: "rgba(220, 20, 60, 0.3)",
                        tension: 0.35,
                    },
                ],
            },
            options: { responsive: true },
        });
    }

    loadPlayerTrend();
}

/* ========================================================================== */
/*                            TEAM DASHBOARD LOGIC                            */
/* ========================================================================== */

let teamPpgChart = null;
let teamRebAstChart = null;
let teamBubble = null;

function initTeamDashboard() {
    console.log("🎯 Initializing Team Dashboard");

    const container = $("#teamDashboard");
    if (!container.dataset.ppg) {
        console.warn("No team stats available yet.");
        return;
    }

    const ppg = Number(container.dataset.ppg);
    const rpg = Number(container.dataset.rpg);
    const apg = Number(container.dataset.apg);

    const l_ppg = Number(container.dataset.leaguePpg);
    const l_rpg = Number(container.dataset.leagueRpg);
    const l_apg = Number(container.dataset.leagueApg);

    /* ---- PPG Comparison Chart ---- */
    destroyIfExists(teamPpgChart);
    teamPpgChart = new Chart($("#teamPpgChart"), {
        type: "bar",
        data: {
            labels: ["Mystics", "League Avg"],
            datasets: [
                {
                    label: "Points Per Game",
                    data: [ppg, l_ppg],
                    backgroundColor: ["#b30000", "#1e3a8a"],
                },
            ],
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });

    /* ---- Rebounds + Assists ---- */
    destroyIfExists(teamRebAstChart);
    teamRebAstChart = new Chart($("#teamRebAstChart"), {
        type: "bar",
        data: {
            labels: ["Rebounds", "Assists"],
            datasets: [
                {
                    label: "Team",
                    data: [rpg, apg],
                    backgroundColor: "#b30000",
                },
                {
                    label: "League Average",
                    data: [l_rpg, l_apg],
                    backgroundColor: "#1e3a8a",
                },
            ],
        },
        options: { responsive: true, scales: { y: { beginAtZero: true } } },
    });

    /* ---- Bubble Demo ---- */
    destroyIfExists(teamBubble);
    teamBubble = new Chart($("#bubbleChart"), {
        type: "bubble",
        data: {
            datasets: [
                {
                    label: "Demo Usage / Efficiency",
                    data: [
                        { x: 20, y: 12, r: 15 },
                        { x: 30, y: 18, r: 20 },
                        { x: 25, y: 10, r: 10 },
                    ],
                    backgroundColor: "rgba(180, 0, 0, 0.4)",
                },
            ],
        },
        options: { responsive: true },
    });

    /* ---- AI Summary ---- */
    $("#aiSummary p").textContent =
        `In ${new Date().getFullYear()}, the Mystics outperform the league average ` +
        `with ${ppg.toFixed(1)} PPG. They generate ${rpg.toFixed(1)} RPG and ` +
        `${apg.toFixed(1)} APG, positioning them competitively in the WNBA league landscape.`;
}

/* ========================================================================== */
/*                         STATS PAGE DEMO CHARTS                             */
/* ========================================================================== */

let demoLine = null;
let demoBar = null;
let demoBubble = null;

function initStatsPage() {
    console.log("🎯 Initializing Stats Demo Page");

    destroyIfExists(demoLine);
    destroyIfExists(demoBar);
    destroyIfExists(demoBubble);

    demoLine = new Chart($("#lineChart"), {
        type: "line",
        data: {
            labels: ["G1", "G2", "G3", "G4", "G5"],
            datasets: [
                {
                    label: "PPG Sample",
                    data: [80, 90, 75, 95, 88],
                    borderColor: "#b30000",
                    backgroundColor: "rgba(180,0,0,0.3)",
                    tension: 0.3,
                },
            ],
        },
    });

    demoBar = new Chart($("#barChart"), {
        type: "bar",
        data: {
            labels: ["Offensive", "Defensive"],
            datasets: [
                {
                    label: "Rating",
                    data: [110, 98],
                    backgroundColor: ["#b30000", "#1e3a8a"],
                },
            ],
        },
    });

    demoBubble = new Chart($("#bubbleChart"), {
        type: "bubble",
        data: {
            datasets: [
                { label: "Demo", data: [{ x: 22, y: 10, r: 12 }] },
            ],
        },
    });

    $("#aiSummary p").textContent =
        "This page demonstrates sample charts using the system-wide styling.";
}

/* ========================================================================== */
/*                          AUTO-INITIALIZER (MASTER)                         */
/* ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    if (isRosterPage) initRosterPage();
    if (isPlayerDetailPage) initPlayerDetailPage();
    if (isTeamDashboard) initTeamDashboard();
    if (isLeagueDashboard) console.log("📊 League dashboard ready (table only).");
    if (isStatsPage) initStatsPage();

    console.log("✅ mystics.js fully loaded.");
});

