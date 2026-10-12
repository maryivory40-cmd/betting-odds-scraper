import argparse

from scraper import OddsPortalScraper
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
        "fetch": scraper.fetch_matches,
        "scan": scraper.scan_arbitrage,
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
            cmd = input("betting-scraper> ").strip().lower()

            if cmd == "scan":
                opportunities = scraper.scan_arbitrage()
            elif cmd in commands:
                commands[cmd]()
            elif cmd == "":
                continue
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
    print("  scan  - Scan fetched matches for arbitrage")
    print("  save  - Save last scan results to CSV")
    print("  help  - Show this help message")
    print("  exit  - Exit the program")
    print("="*50 + "\n")


def exit_program():
    print("\n👋 Goodbye!\n")
    exit(0)


if __name__ == "__main__":
    main()
