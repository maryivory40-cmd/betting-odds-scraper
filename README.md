# betting-odds-scraper

A Python-based betting odds scraper and arbitrage scanner.

## Features
- Fetch Premier League fixture odds from OddsPortal
- Parse odds and detect arbitrage opportunities
- Read visible text from betting screenshots sent to the Telegram bot
- View match odds and estimated market-implied probabilities in a mobile-friendly web dashboard
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

## Telegram bot

Create a bot with Telegram's [@BotFather](https://t.me/BotFather) and copy its
token. Set the token and your Telegram numeric user ID before starting the bot.
You can start the bot and send `/id` to see your ID; until an ID is configured,
only `/start` and `/id` are available.

```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_ALLOWED_USER_IDS="123456789"
python main.py --telegram
```

For multiple authorized users, provide comma-separated IDs in
`TELEGRAM_ALLOWED_USER_IDS`. Keep the bot token private. The bot uses long
polling, so it can run on a computer or server without a public webhook URL.
Send `/fetch`, `/scan`, and `/save` in Telegram to perform the corresponding
scraper actions; `/help` lists the commands. Send a screenshot as a photo or a
JPEG/PNG image document to have the bot extract its visible text. The bot uses
Tesseract OCR; the included Dockerfile installs it for deployment. OCR can
misread team names or odds, so verify all extracted text. Screenshot reading
does not connect to bookmaker accounts, create bet slips, or place bets.

## Web dashboard

Start the dashboard locally with:

```bash
python main.py --web
```

Then open `http://127.0.0.1:8000`. To allow access from other devices on the same
network, bind to your computer's network interface with `--host 0.0.0.0`; for
example, run `python main.py --web --host 0.0.0.0 --port 8000` and visit the
computer's LAN address from your phone. Do not expose the server directly to
the public internet without adding suitable production hosting and security.

The dashboard currently shows the scraper's EPL odds and the normalized
market-implied probabilities derived from those same odds. These are not
independent match predictions and are not validated against historical data;
they cannot guarantee an outcome. OddsPortal availability and parsed fixtures
may vary.

The included Docker image can also run the website:

```bash
docker run --rm -p 8000:8000 betting-odds-scraper:ocr \
  python main.py --web --host 0.0.0.0
```

## Example commands
- `fetch` - Fetch matches from OddsPortal
- `scan` - Scan for arbitrage opportunities
- `save` - Save results to CSV
- `exit` - Exit the program
