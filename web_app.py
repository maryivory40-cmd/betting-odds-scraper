import json
import math
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from scraper import LEAGUES

WEB_DIR = Path(__file__).parent / "web"


def market_probabilities(match):
    """Return normalized market-implied probabilities from decimal odds."""
    try:
        odds = [float(match[key]) for key in ("home", "draw", "away")]
    except (KeyError, TypeError, ValueError):
        return None

    if any(not math.isfinite(value) or value <= 1 for value in odds):
        return None

    implied = [1 / value for value in odds]
    total = sum(implied)
    return {
        key: value / total * 100
        for key, value in zip(("home", "draw", "away"), implied)
    }


class OddsDashboardHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, scraper, **kwargs):
        self.scraper = scraper
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_path = urlsplit(self.path)
        if parsed_path.path == "/api/matches":
            query = parse_qs(parsed_path.query)
            league = query.get("league", ["premier-league"])[0]
            if league not in LEAGUES:
                self._send_json(400, {"error": "Choose a supported league."})
                return
            self._serve_matches(league)
            return

        if parsed_path.query:
            self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
            return

        if parsed_path.path == "/":
            asset = ("index.html", "text/html; charset=utf-8")
        else:
            asset = {
                "/styles.css": ("styles.css", "text/css; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript; charset=utf-8"),
            }.get(parsed_path.path)
        if asset is None:
            self._send_bytes(404, b"Not found", "text/plain; charset=utf-8")
            return

        filename, content_type = asset
        try:
            content = (WEB_DIR / filename).read_bytes()
        except OSError:
            self._send_bytes(
                500, b"Dashboard files are unavailable.", "text/plain; charset=utf-8"
            )
            return
        self._send_bytes(200, content, content_type)

    def _serve_matches(self, league):
        selected_league = LEAGUES[league]
        try:
            matches = self.scraper.fetch_matches(url=selected_league["url"])
        except Exception:
            self._send_json(
                502,
                {"error": "Odds are temporarily unavailable. Please try again."},
            )
            return

        result = []
        for match in matches:
            probabilities = market_probabilities(match)
            if probabilities is not None:
                odds = {
                    key: float(match[key]) for key in ("home", "draw", "away")
                }
                result.append(
                    {
                        "teams": str(match.get("teams", "Match")),
                        "odds": odds,
                        "probabilities": probabilities,
                    }
                )

        self._send_json(
            200,
            {
                "league": league,
                "league_name": selected_league["name"],
                "matches": result,
                "disclaimer": (
                    "Estimates are normalized market-implied probabilities from "
                    "the displayed odds, not independently validated predictions."
                ),
            },
        )

    def _send_json(self, status, payload):
        self._send_bytes(
            status,
            json.dumps(payload, allow_nan=False).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def _send_bytes(self, status, content, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; connect-src 'self'; style-src 'self'; "
            "script-src 'self'; img-src 'self' data:; base-uri 'none'; "
            "frame-ancestors 'none'",
        )
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(content)


def create_server(host, port, scraper):
    handler = partial(OddsDashboardHandler, scraper=scraper)
    return ThreadingHTTPServer((host, port), handler)
