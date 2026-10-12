# betting Bot

A Python-based betting odds scraper and arbitrage scanner.

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
- `repl` - Open an interactive Python REPL with `scraper` and `opportunities`
- `exit` - Exit the program
