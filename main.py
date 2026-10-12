import code

from scraper import OddsPortalScraper


def main():
    scraper = OddsPortalScraper()
    opportunities = []

    commands = {
        "fetch": scraper.fetch_matches,
        "scan": scraper.scan_arbitrage,
        "save": lambda: scraper.save_results(opportunities),
        "repl": lambda: start_python_repl(scraper, opportunities),
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
    print("  repl  - Open an interactive Python REPL")
    print("  help  - Show this help message")
    print("  exit  - Exit the program")
    print("="*50 + "\n")


def start_python_repl(scraper, opportunities):
    print("\n🐍 Python REPL started. Press Ctrl-D to return to the CLI.\n")
    banner = "Available objects: scraper, opportunities"
    code.interact(banner=banner, local={"scraper": scraper, "opportunities": opportunities})


def exit_program():
    print("\n👋 Goodbye!\n")
    exit(0)


if __name__ == "__main__":
    main()
