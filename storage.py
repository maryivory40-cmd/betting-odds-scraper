import csv
from pathlib import Path


class OddsStorage:
    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_matches(self, matches, filename="matches.csv"):
        path = self.output_dir / filename
        fieldnames = ["teams", "home", "draw", "away", "implied_total", "profit_percent"]

        with path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for match in matches:
                writer.writerow({
                    "teams": match.get("teams", ""),
                    "home": match.get("home", ""),
                    "draw": match.get("draw", ""),
                    "away": match.get("away", ""),
                    "implied_total": match.get("implied_total", ""),
                    "profit_percent": match.get("profit_percent", ""),
                })

        print(f"Saved matches to {path}")
