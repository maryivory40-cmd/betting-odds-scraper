const matchesElement = document.querySelector("#matches");
const messageElement = document.querySelector("#message");
const countElement = document.querySelector("#match-count");
const updatedElement = document.querySelector("#updated");
const refreshButton = document.querySelector("#refresh");
const leagueSelect = document.querySelector("#league-select");
const leagueLabel = document.querySelector("#league-label");

function addMarket(card, label, odds, probability) {
  const market = document.createElement("div");
  market.className = "market";

  const top = document.createElement("div");
  top.className = "market-top";
  const marketName = document.createElement("span");
  marketName.textContent = label;
  const marketOdds = document.createElement("strong");
  marketOdds.textContent = odds.toFixed(2);
  top.append(marketName, marketOdds);

  const percent = document.createElement("span");
  percent.className = "market-probability";
  percent.textContent = `${probability.toFixed(1)}%`;

  const track = document.createElement("div");
  track.className = "probability-track";
  track.setAttribute("aria-label", `${label} estimated market probability`);
  const fill = document.createElement("div");
  fill.className = "probability-fill";
  fill.style.width = `${Math.max(0, Math.min(100, probability))}%`;
  track.append(fill);
  market.append(top, percent, track);
  card.append(market);
}

function renderMatches(matches, leagueName) {
  matchesElement.replaceChildren();
  countElement.textContent = `${matches.length} ${matches.length === 1 ? "match" : "matches"}`;
  leagueLabel.textContent = leagueName.toUpperCase();

  if (!matches.length) {
    messageElement.textContent =
      "No readable match odds are available right now. The source may have no listed fixtures or its page may have changed.";
    messageElement.hidden = false;
    return;
  }

  messageElement.hidden = true;
  for (const match of matches) {
    const card = document.createElement("article");
    card.className = "match-card";

    const title = document.createElement("h3");
    title.className = "match-title";
    title.textContent = match.teams;

    const grid = document.createElement("div");
    grid.className = "market-grid";
    addMarket(grid, "HOME", match.odds.home, match.probabilities.home);
    addMarket(grid, "DRAW", match.odds.draw, match.probabilities.draw);
    addMarket(grid, "AWAY", match.odds.away, match.probabilities.away);
    card.append(title, grid);
    matchesElement.append(card);
  }

  updatedElement.textContent = `Odds loaded ${new Date().toLocaleTimeString()}`;
}

async function loadMatches() {
  refreshButton.disabled = true;
  refreshButton.setAttribute("aria-busy", "true");
  messageElement.hidden = false;
  messageElement.textContent = "Loading the latest available odds…";
  updatedElement.textContent = "";

  try {
    const response = await fetch(
      `/api/matches?league=${encodeURIComponent(leagueSelect.value)}`,
      { headers: { Accept: "application/json" } },
    );
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Odds are temporarily unavailable.");
    }
    renderMatches(data.matches, data.league_name);
  } catch (error) {
    matchesElement.replaceChildren();
    countElement.textContent = "—";
    messageElement.textContent =
      error.message || "Could not load odds. Please try again.";
    messageElement.hidden = false;
  } finally {
    refreshButton.disabled = false;
    refreshButton.removeAttribute("aria-busy");
  }
}

refreshButton.addEventListener("click", loadMatches);
leagueSelect.addEventListener("change", loadMatches);
loadMatches();
