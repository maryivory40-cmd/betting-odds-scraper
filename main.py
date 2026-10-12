import argparse

from scraper import LEAGUES, OddsPortalScraper
from telegram_bot import TelegramBot
from web_app import create_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Run the Telegram bot instead of the command-line interface",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Run the mobile-friendly odds dashboard",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Web dashboard bind address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Web dashboard port (default: 8000)",
    )
    args = parser.parse_args()

    if args.web:
        server = create_server(args.host, args.port, OddsPortalScraper())
        print(f"Odds dashboard running at http://{args.host}:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nOdds dashboard stopped.")
        finally:
            server.server_close()
        return

    if args.telegram:
        TelegramBot.from_environment().run()
        return

    scraper = OddsPortalScraper()
    opportunities = []

    commands = {
        "save": lambda: scraper.save_results(opportunities),
        "help": show_help,
        "exit": lambda: exit_program(),
    }

    print("\n" + "="*50)
    print("🎯 Betting Odds Scraper & Arbitrage Scanner")
    print("="*50)
    print("Type 'help' for available commands\n")

    while True:
        try:
            parts = input("betting-scraper> ").strip().lower().split()
            if not parts:
                continue
            cmd = parts[0]
            league_key = parts[1] if len(parts) > 1 else "premier-league"

            if cmd in {"fetch", "scan"}:
                league = LEAGUES.get(league_key)
                if not league:
                    print("Unknown league. Type 'help' to see available league keys.")
                    continue
                league_url = league["url"]
                if cmd == "scan":
                    opportunities = scraper.scan_arbitrage(url=league_url)
                else:
                    scraper.fetch_matches(url=league_url)
            elif cmd in commands:
                commands[cmd]()
            else:
                print("❓ Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\n✋ Interrupted. Type 'exit' to quit.")
        except Exception as e:
            print(f"❌ Error: {e}")


def show_help():
    print("\n" + "="*50)
    print("Available Commands:")
    print("="*50)
    print("  fetch - Fetch matches from OddsPortal")
    print("  scan  - Scan matches for arbitrage")
    print("  Use fetch <league> or scan <league> with:")
    for key, league in LEAGUES.items():
        print(f"    {key} - {league['name']}")
    print("  save  - Save last scan results to CSV")
    print("  help  - Show this help message")
    print("  exit  - Exit the program")
    print("="*50 + "\n")


def exit_program():
    print("\n👋 Goodbye!\n")
    exit(0)


if __name__ == "__main__":
    main()
