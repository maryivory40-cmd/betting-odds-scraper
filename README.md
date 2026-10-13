# Betting Odds Scraper

A Python-based betting odds scraper and arbitrage scanner.

## Defensive cybersecurity research workspace

This repository also includes a local-first prototype for defensive cybersecurity research. It combines curated links to trusted security resources, a browser-local research notebook, and a local discussion board.

Run it with Python:

```bash
python research_app.py
```

Then open `http://127.0.0.1:8000`. Use `python research_app.py --port 8080` to select another port. The server binds to localhost; notebook entries and discussion posts are stored in the current browser only and are not shared with other users. The resource search covers its curated catalog rather than the entire web. This prototype does not provide accounts, live chat, or security scanning and makes no claim to be unhackable. Use any security guidance only for systems you own or are authorized to assess.

## Features
- Fetch Premier League fixture odds from OddsPortal
- Parse odds and detect arbitrage opportunities
- Save results to CSV
- Command-line interface

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Example commands
- `fetch` - Fetch matches from OddsPortal
- `scan` - Scan for arbitrage opportunities
- `save` - Save results to CSV
- `exit` - Exit the program
