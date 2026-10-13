"""Run the local defensive cybersecurity research workspace."""

from argparse import ArgumentParser, ArgumentTypeError
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


APP_DIRECTORY = Path(__file__).resolve().parent / "cyber_research"
LOCAL_HOST = "127.0.0.1"


def valid_port(value):
    try:
        port = int(value)
    except ValueError as exc:
        raise ArgumentTypeError("port must be an integer between 1 and 65535") from exc
    if not 1 <= port <= 65535:
        raise ArgumentTypeError("port must be between 1 and 65535")
    return port


class ResearchRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        super().end_headers()


def main():
    parser = ArgumentParser(description="Run the local defensive cybersecurity research workspace.")
    parser.add_argument("--port", type=valid_port, default=8000, help="Local web server port (default: 8000)")
    args = parser.parse_args()

    if not (APP_DIRECTORY / "index.html").is_file():
        parser.error(f"workspace page not found: {APP_DIRECTORY / 'index.html'}")

    handler = partial(ResearchRequestHandler, directory=str(APP_DIRECTORY))

    try:
        server = ThreadingHTTPServer((LOCAL_HOST, args.port), handler)
    except OSError as exc:
        parser.error(f"could not start local server on port {args.port}: {exc}")

    with server:
        actual_port = server.server_address[1]
        print(f"Research workspace running at http://{LOCAL_HOST}:{actual_port}")
        print("Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nResearch workspace stopped.")


if __name__ == "__main__":
    main()
