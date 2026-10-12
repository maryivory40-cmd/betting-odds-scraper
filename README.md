# betting-odds-scraper

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
scraper actions; `/help` lists the commands.

## Example commands
- `fetch` - Fetch matches from OddsPortal
- `scan` - Scan for arbitrage opportunities
- `save` - Save results to CSV
- `exit` - Exit the program
