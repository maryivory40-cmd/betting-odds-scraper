"""Run the local defensive cybersecurity research workspace."""

from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_DIRECTORY = Path(__file__).resolve().parent / "cyber_research"


class ResearchRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        super().end_headers()


def main():
    parser = ArgumentParser(description="Run the local defensive cybersecurity research workspace.")
    parser.add_argument("--port", type=int, default=8000, help="Local web server port (default: 8000)")
    args = parser.parse_args()
    handler = partial(ResearchRequestHandler, directory=str(APP_DIRECTORY))

    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        print(f"Research workspace running at http://127.0.0.1:{args.port}")
        print("Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nResearch workspace stopped.")


if __name__ == "__main__":
    main()
