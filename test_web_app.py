import json
import re
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from scraper import LEAGUES
from web_app import WEB_DIR, create_server, market_probabilities


class OddsDashboardTests(unittest.TestCase):
    def test_normalizes_odds_to_market_implied_percentages(self):
        probabilities = market_probabilities(
            {"home": 2.0, "draw": 3.0, "away": 4.0}
        )

        self.assertAlmostEqual(sum(probabilities.values()), 100)
        self.assertAlmostEqual(probabilities["home"], 46.1538, places=3)
        self.assertGreater(probabilities["home"], probabilities["draw"])
        self.assertGreater(probabilities["draw"], probabilities["away"])

    def test_rejects_missing_nonpositive_and_nonfinite_odds(self):
        for match in (
            {"home": 2.0, "draw": 3.0},
            {"home": 0, "draw": 3.0, "away": 4.0},
            {"home": 1.0, "draw": 3.0, "away": 4.0},
            {"home": float("inf"), "draw": 3.0, "away": 4.0},
        ):
            with self.subTest(match=match):
                self.assertIsNone(market_probabilities(match))

    def test_api_returns_match_odds_and_disclaimer(self):
        requested_urls = []

        class FakeScraper:
            def fetch_matches(self, url=None):
                requested_urls.append(url)
                return [
                    {
                        "teams": "Team A - Team B",
                        "home": 2.0,
                        "draw": 3.0,
                        "away": 4.0,
                    }
                ]

        server = create_server("127.0.0.1", 0, FakeScraper())
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with urlopen(
                f"http://127.0.0.1:{server.server_port}/api/matches?league=serie-a"
            ) as resp:
                payload = json.load(resp)
            self.assertEqual(payload["league"], "serie-a")
            self.assertEqual(payload["league_name"], "Serie A")
            self.assertEqual(requested_urls, [LEAGUES["serie-a"]["url"]])
            self.assertEqual(payload["matches"][0]["teams"], "Team A - Team B")
            self.assertIn("not independently validated", payload["disclaimer"])
            self.assertEqual(resp.headers["X-Content-Type-Options"], "nosniff")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_api_rejects_unknown_league(self):
        class FakeScraper:
            def fetch_matches(self, url=None):
                raise AssertionError("Unknown league must not be fetched")

        server = create_server("127.0.0.1", 0, FakeScraper())
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with self.assertRaises(HTTPError) as error:
                urlopen(
                    f"http://127.0.0.1:{server.server_port}/api/matches?league=invalid"
                )
            self.assertEqual(error.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_league_catalog_covers_requested_and_major_european_competitions(self):
        self.assertEqual(
            set(LEAGUES),
            {
                "premier-league",
                "laliga",
                "serie-a",
                "bundesliga",
                "ligue-1",
                "champions-league",
                "europa-league",
                "conference-league",
            },
        )

    def test_website_selector_matches_supported_league_catalog(self):
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        options = re.findall(r'<option value="([^"]+)"', html)

        self.assertEqual(set(options), set(LEAGUES))

    def test_unknown_routes_are_not_served(self):
        class FakeScraper:
            def fetch_matches(self):
                return []

        server = create_server("127.0.0.1", 0, FakeScraper())
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with self.assertRaises(HTTPError) as error:
                urlopen(f"http://127.0.0.1:{server.server_port}/../README.md")
            self.assertEqual(error.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
