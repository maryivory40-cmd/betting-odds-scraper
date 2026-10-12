import csv
from pathlib import Path
from datetime import datetime


class OddsStorage:
    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_matches(self, matches, filename=None):
        """Save matches to CSV with timestamp"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arbitrage_{timestamp}.csv"

        path = self.output_dir / filename
        fieldnames = ["teams", "home", "draw", "away", "implied_total", "profit_percent"]

        try:
            with path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for match in matches:
                    writer.writerow({
                        "teams": match.get("teams", ""),
                        "home": f"{match.get('home', ''):.2f}",
                        "draw": f"{match.get('draw', ''):.2f}",
                        "away": f"{match.get('away', ''):.2f}",
                        "implied_total": f"{match.get('implied_total', ''):.4f}",
                        "profit_percent": f"{match.get('profit_percent', ''):.2f}",
                    })

            print(f"💾 Saved {len(matches)} matches to {path}")
        except IOError as exc:
            print(f"Error saving file: {exc}")
