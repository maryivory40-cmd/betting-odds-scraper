import requests
from bs4 import BeautifulSoup
import time


class OddsPortalScraper:
    def __init__(self, url="https://www.oddsportal.com/soccer/england/premier-league/"):
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.matches = []

    def fetch_matches(self):
        """Fetch matches from OddsPortal"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to fetch page: {exc}") from exc

        self.matches = self._parse_matches(response.text)

        if self.matches:
            print(f"✅ Fetched {len(self.matches)} matches")
        else:
            print(
                "⚠️ No parseable matches found. The page may have no listed "
                "fixtures or its layout may have changed."
            )

        return self.matches

    @staticmethod
    def _parse_matches(html):
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("tr.odd, tr.even")
        matches = []
        for row in rows:
            try:
                teams_elem = row.select_one("td.name, td.table-participant")
                if not teams_elem:
                    continue

                teams = teams_elem.text.strip()
                odds_cells = row.select("td.odds-nowrp")
                if len(odds_cells) < 3:
                    continue

                home = float(odds_cells[0].text.strip())
                draw = float(odds_cells[1].text.strip())
                away = float(odds_cells[2].text.strip())

                matches.append({
                    "teams": teams,
                    "home": home,
                    "draw": draw,
                    "away": away,
                })
            except (TypeError, ValueError, AttributeError):
                continue

        return matches

    def scan_arbitrage(self):
        """Scan matches for arbitrage opportunities"""
        if not self.matches:
            self.fetch_matches()
        if not self.matches:
            print("No match odds available to scan.")
            return []

        opportunities = []
        for match in self.matches:
            home = match["home"]
            draw = match["draw"]
            away = match["away"]
            implied_total = (1 / home) + (1 / draw) + (1 / away)

            if implied_total < 1:
                profit_percent = (1 / implied_total - 1) * 100
                opportunities.append({
                    "teams": match["teams"],
                    "home": home,
                    "draw": draw,
                    "away": away,
                    "implied_total": implied_total,
                    "profit_percent": profit_percent,
                })

        if opportunities:
            print(f"\n🚨 Found {len(opportunities)} arbitrage opportunity(ies):\n")
            for opp in opportunities:
                print(f"🚨 ARBITRAGE FOUND: {opp['teams']}")
                print(f"Home: {opp['home']}, Draw: {opp['draw']}, Away: {opp['away']}")
                print(f"Profit: {opp['profit_percent']:.2f}%\n")
        else:
            print("\n❌ No arbitrage opportunities found.\n")

        return opportunities

    def save_results(self, opportunities=None):
        """Save arbitrage opportunities to CSV"""
        from storage import OddsStorage

        if opportunities is None:
            opportunities = self.scan_arbitrage()

        if opportunities:
            storage = OddsStorage()
            storage.save_matches(opportunities)
        else:
            print("No opportunities to save.")
