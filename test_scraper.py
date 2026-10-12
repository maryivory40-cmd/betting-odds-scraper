import unittest
from unittest.mock import Mock, patch

from scraper import LEAGUES, OddsPortalScraper


class OddsPortalParserTests(unittest.TestCase):
    def test_parses_odd_even_and_legacy_fixture_rows(self):
        html = """
        <table>
          <tr class="odd">
            <td class="table-participant">Team A - Team B</td>
            <td class="odds-nowrp">2.10</td>
            <td class="odds-nowrp">3.40</td>
            <td class="odds-nowrp">3.60</td>
          </tr>
          <tr class="even">
            <td class="name">Team C - Team D</td>
            <td class="odds-nowrp">1.80</td>
            <td class="odds-nowrp">3.20</td>
            <td class="odds-nowrp">4.50</td>
          </tr>
          <tr class="odd deactivate">
            <td class="name">Team E - Team F</td>
            <td class="odds-nowrp">2.00</td>
            <td class="odds-nowrp">3.00</td>
            <td class="odds-nowrp">4.00</td>
          </tr>
        </table>
        """

        self.assertEqual(
            OddsPortalScraper._parse_matches(html),
            [
                {"teams": "Team A - Team B", "home": 2.1, "draw": 3.4, "away": 3.6},
                {"teams": "Team C - Team D", "home": 1.8, "draw": 3.2, "away": 4.5},
                {"teams": "Team E - Team F", "home": 2.0, "draw": 3.0, "away": 4.0},
            ],
        )

    def test_skips_rows_without_three_valid_odds(self):
        html = """
        <tr class="odd">
          <td class="name">Team A - Team B</td>
          <td class="odds-nowrp">2.10</td>
          <td class="odds-nowrp">N/A</td>
          <td class="odds-nowrp">3.60</td>
        </tr>
        """

        self.assertEqual(OddsPortalScraper._parse_matches(html), [])

    def test_empty_page_returns_no_matches(self):
        self.assertEqual(OddsPortalScraper._parse_matches("<html></html>"), [])

    @patch("scraper.requests.get")
    def test_fetch_matches_uses_selected_competition_url(self, mock_get):
        response = Mock(text="<html></html>")
        mock_get.return_value = response
        scraper = OddsPortalScraper()

        scraper.fetch_matches(url=LEAGUES["laliga"]["url"])

        mock_get.assert_called_once_with(
            LEAGUES["laliga"]["url"], headers=scraper.headers, timeout=15
        )
        response.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
