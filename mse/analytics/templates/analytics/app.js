// ---------------------------------------------
// MOCK PLAYER DATA (replace with real Mystics roster later)
// ---------------------------------------------
const mysticsPlayers = [
    {
        id: "player_atkins",
        name: "Ariel Atkins",
        age: 28,
        height: "5'11\"",
        weight: "167 lbs",
        jersey: 7,
        photo: "images/ariel-atkins.jpg"
    },
    {
        id: "player_sykes",
        name: "Brittney Sykes",
        age: 30,
        height: "5'9\"",
        weight: "154 lbs",
        jersey: 15,
        photo: "images/brittney-sykes.jpg"
    },
    {
        id: "player_austin",
        name: "Shakira Austin",
        age: 24,
        height: "6'5\"",
        weight: "190 lbs",
        jersey: 0,
        photo: "images/shakira-austin.jpg"
    },
    {
        id: "player_cloud",
        name: "Natasha Cloud",
        age: 32,
        height: "5'9\"",
        weight: "160 lbs",
        jersey: 9,
        photo: "images/natasha-cloud.jpg"
    },
    // Add more players as needed
];

// ---------------------------------------------
// INIT ROSTER SELECT + DETAIL VIEW
// ---------------------------------------------
function initRosterPage() {
    const selectEl = document.getElementById("playerSelect");
    const nameEl = document.getElementById("playerName");
    const jerseyEl = document.getElementById("playerJersey");
    const ageEl = document.getElementById("playerAge");
    const heightEl = document.getElementById("playerHeight");
    const weightEl = document.getElementById("playerWeight");
    const photoEl = document.getElementById("playerPhoto");

    if (!selectEl || !nameEl || !jerseyEl) {
        // Not on roster page
        return;
    }

    // Populate select options
    selectEl.innerHTML = "";
    mysticsPlayers.forEach(player => {
        const opt = document.createElement("option");
        opt.value = player.id;
        opt.textContent = player.name;
        selectEl.appendChild(opt);
    });

    // Helper to set detail content
    const renderPlayer = (playerId) => {
        const player = mysticsPlayers.find(p => p.id === playerId);
        if (!player) return;

        nameEl.textContent = player.name;
        jerseyEl.textContent = `#${player.jersey}`;
        ageEl.textContent = player.age;
        heightEl.textContent = player.height;
        weightEl.textContent = player.weight;
        photoEl.src = player.photo;
        photoEl.alt = `${player.name} photo`;
    };

    // Initial selection
    if (mysticsPlayers.length > 0) {
        renderPlayer(mysticsPlayers[0].id);
        selectEl.value = mysticsPlayers[0].id;
    }

    // On change
    selectEl.addEventListener("change", (e) => {
        renderPlayer(e.target.value);
    });
}

// ---------------------------------------------
// INIT CHARTS ON STATS PAGE
// ---------------------------------------------
function initCharts() {
    const lineCanvas = document.getElementById("lineChart");
    const barCanvas = document.getElementById("barChart");
    const bubbleCanvas = document.getElementById("bubbleChart");

    if (!lineCanvas || !barCanvas || !bubbleCanvas || typeof Chart === "undefined") {
        // Not on stats page or Chart.js not loaded
        return;
    }

    // Sample data – replace with real season stats if hooked to API
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

    // BUBBLE CHART – Usage vs Efficiency vs Minutes (bubble size)
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

    // Simple AI-style summary based on sample stats
    generateAISummary({ mysticsPPG, leagueAvgPPG, offensiveRating, defensiveRating });
}

// ---------------------------------------------
// SIMPLE "AI-STYLE" SUMMARY (FRONTEND MOCK)
// ---------------------------------------------
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

// ---------------------------------------------
// DOM READY
// ---------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    initRosterPage();
    initCharts();
});
