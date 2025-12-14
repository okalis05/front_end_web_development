document.addEventListener("DOMContentLoaded", () => {
    initThemeToggle();
    initRosterPage();
    initPlayerChart();
    initCharts();
});

/* THEME TOGGLE (uses localStorage) */
function initThemeToggle() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
        document.body.classList.add("dark-mode");
    }

    btn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        const isDark = document.body.classList.contains("dark-mode");
        localStorage.setItem("theme", isDark ? "dark" : "light");
    });
}

/* ROSTER PAGE – DETAIL CARD & PHOTO */
function initRosterPage() {
    const selectEl = document.getElementById("playerSelect");
    const detailEl = document.getElementById("playerDetail");
    if (!selectEl || !detailEl) return; // not on roster page

    const photoEl = document.getElementById("playerPhoto");
    const nameEl = document.getElementById("playerName");
    const jerseyEl = document.getElementById("playerJersey");
    const ageEl = document.getElementById("playerAge");
    const heightEl = document.getElementById("playerHeight");
    const weightEl = document.getElementById("playerWeight");

    const players = JSON.parse(detailEl.dataset.players);
    const defaultPhotoUrl = detailEl.dataset.defaultPhotoUrl;

    function renderPlayer(id) {
        const p = players.find(pl => pl.id === parseInt(id));
        if (!p) return;

        nameEl.textContent = p.name;
        jerseyEl.textContent = "#" + (p.jersey || "--");
        ageEl.textContent = p.age || "–";
        heightEl.textContent = p.height || "–";
        weightEl.textContent = p.weight || "–";

        if (p.headshot) {
            photoEl.src = p.headshot;
        } else {
            photoEl.src = defaultPhotoUrl;
        }
    }

    if (players.length) {
        selectEl.value = players[0].id;
        renderPlayer(players[0].id);
    }

    selectEl.addEventListener("change", (e) => {
        renderPlayer(e.target.value);
        updatePlayerTrendChart();
    });
}

/* PLAYER TREND CHART (Roster page) */
let playerTrendChart = null;

function initPlayerChart() {
    const canvas = document.getElementById("playerTrendChart");
    const selectEl = document.getElementById("playerSelect");
    if (!canvas || !selectEl || typeof Chart === "undefined") return;

    const ctx = canvas.getContext("2d");
    playerTrendChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Points",
                data: [],
                tension: 0.3,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    updatePlayerTrendChart();
}

function updatePlayerTrendChart() {
    if (!playerTrendChart) return;

    const selectEl = document.getElementById("playerSelect");
    const urlTemplate = selectEl.dataset.playerChartUrl; // /api/player/0/game-log/
    const playerId = selectEl.value;
    const url = urlTemplate.replace("/0/", `/${playerId}/`);

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const labels = data.games.map(g => g.date.slice(5)); // MM-DD
            const points = data.games.map(g => g.points);

            playerTrendChart.data.labels = labels;
            playerTrendChart.data.datasets[0].data = points;
            playerTrendChart.update();
        })
        .catch(err => console.error("Trend chart error", err));
}

/* DASHBOARD/STATS CHARTS USING SAMPLE DATA */
function initCharts() {
    const lineCanvas = document.getElementById("lineChart");
    const barCanvas = document.getElementById("barChart");
    const bubbleCanvas = document.getElementById("bubbleChart");

    if (!lineCanvas || !barCanvas || !bubbleCanvas || typeof Chart === "undefined") {
        return; // not on charts page or Chart.js missing
    }

    // Sample data – replace with real season stats later
    const games = ["Game 1", "Game 2", "Game 3", "Game 4", "Game 5", "Game 6"];
    const mysticsPPG = [78, 82, 75, 88, 80, 84];
    const leagueAvgPPG = [80, 81, 79, 82, 81, 83];

    // LINE CHART – Points Per Game
    new Chart(lineCanvas.getContext("2d"), {
        type: "line",
        data: {
            labels: games,
            datasets: [
                {
                    label: "Mystics PPG",
                    data: mysticsPPG,
                    tension: 0.3
                },
                {
                    label: "League Avg PPG",
                    data: leagueAvgPPG,
                    borderDash: [5, 5],
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    // BAR CHART – Offensive vs Defensive Rating
    const teams = ["Mystics", "Team A", "Team B", "Team C", "Team D"];
    const offensiveRating = [101, 98, 104, 99, 102];
    const defensiveRating = [97, 102, 99, 101, 100];

    new Chart(barCanvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: teams,
            datasets: [
                {
                    label: "Offensive Rating",
                    data: offensiveRating
                },
                {
                    label: "Defensive Rating (lower is better)",
                    data: defensiveRating
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });

    // BUBBLE CHART – Usage vs Efficiency vs Minutes
    const bubbleData = [
        { label: "Mystics", x: 24, y: 1.08, r: 14 },
        { label: "Team A", x: 21, y: 1.02, r: 12 },
        { label: "Team B", x: 26, y: 1.05, r: 16 },
        { label: "Team C", x: 19, y: 1.00, r: 10 },
        { label: "Team D", x: 23, y: 1.03, r: 13 }
    ];

    new Chart(bubbleCanvas.getContext("2d"), {
        type: "bubble",
        data: {
            datasets: bubbleData.map(team => ({
                label: team.label,
                data: [{ x: team.x, y: team.y, r: team.r }]
            }))
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                x: {
                    title: { display: true, text: "Usage Rate (%)" }
                },
                y: {
                    title: { display: true, text: "Points per Possession" }
                }
            }
        }
    });

    generateAISummary({ mysticsPPG, leagueAvgPPG, offensiveRating, defensiveRating });
}

function generateAISummary({ mysticsPPG, leagueAvgPPG, offensiveRating, defensiveRating }) {
    const summaryEl = document.getElementById("aiSummary");
    if (!summaryEl) return;

    const avgMysticsPPG = average(mysticsPPG);
    const avgLeaguePPG = average(leagueAvgPPG);
    const mysticsOff = offensiveRating[0];
    const mysticsDef = defensiveRating[0];

    let scoringTrend;
    if (avgMysticsPPG > avgLeaguePPG + 1.5) {
        scoringTrend = "outscoring the league average and trending as an above-average offense.";
    } else if (avgMysticsPPG < avgLeaguePPG - 1.5) {
        scoringTrend = "slightly below league scoring norms, suggesting room for offensive optimization.";
    } else {
        scoringTrend = "tracking very close to league scoring norms, indicating balanced offensive output.";
    }

    let defenseNote;
    if (mysticsDef < average(defensiveRating)) {
        defenseNote = "a relative defensive strength compared with peer teams.";
    } else {
        defenseNote = "an area where targeted adjustments could generate additional wins.";
    }

    const html = `
        <h3>AI-Generated Summary</h3>
        <p>
            Across the recent sample of games, the Washington Mystics are averaging
            <strong>${avgMysticsPPG.toFixed(1)} points per game</strong> versus a league
            benchmark of <strong>${avgLeaguePPG.toFixed(1)}</strong>,
            ${scoringTrend}
        </p>
        <p>
            With an estimated offensive rating of <strong>${mysticsOff}</strong> and
            defensive rating near <strong>${mysticsDef}</strong>, the data signals
            <strong>${defenseNote}</strong>
        </p>
        <p>
            Combined, these trends suggest that incremental improvements in efficiency—
            particularly in half-court sets and late-game possessions—could meaningfully
            shift the Mystics’ win probability profile over the remainder of the season.
        </p>
    `;
    summaryEl.innerHTML = html;
}

function average(arr) {
    if (!arr || arr.length === 0) return 0;
    const sum = arr.reduce((acc, v) => acc + v, 0);
    return sum / arr.length;
}


