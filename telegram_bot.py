import os
import subprocess
import tempfile
import time

import requests

from scraper import OddsPortalScraper


class TelegramBot:
    def __init__(self, token, allowed_user_ids, scraper=None):
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.file_api_url = f"https://api.telegram.org/file/bot{token}"
        self.allowed_user_ids = allowed_user_ids
        self.scraper = scraper or OddsPortalScraper()
        self.opportunities = []

    @classmethod
    def from_environment(cls):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("Set the TELEGRAM_BOT_TOKEN environment variable.")

        allowed_user_ids = {
            int(user_id.strip())
            for user_id in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
            if user_id.strip()
        }
        return cls(token, allowed_user_ids)

    def _api_request(self, method, data=None, timeout=15):
        try:
            response = requests.post(
                f"{self.api_url}/{method}", data=data, timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise RuntimeError("Telegram API request failed.") from exc

        if not result.get("ok"):
            raise RuntimeError("Telegram API request failed.")
        return result["result"]

    def _send_message(self, chat_id, text):
        self._api_request("sendMessage", {"chat_id": chat_id, "text": text})

    def _handle_update(self, update):
        message = update.get("message", {})
        text = (message.get("text") or "").strip()
        sender = message.get("from", {})
        chat_id = message.get("chat", {}).get("id")
        user_id = sender.get("id")
        if chat_id is None or user_id is None:
            return

        if not text.startswith("/"):
            if not message.get("photo") and not self._is_supported_image_document(message):
                return
            if user_id not in self.allowed_user_ids:
                self._send_message(chat_id, "You are not authorized to use this bot.")
                return
            self._handle_screenshot(message, chat_id)
            return

        command = text.split()[0][1:].split("@", 1)[0].lower()
        if command in {"start", "id"}:
            if user_id in self.allowed_user_ids:
                self._send_message(chat_id, "Bot is ready. Send /help for commands.")
            else:
                self._send_message(
                    chat_id,
                    f"Your Telegram user ID is {user_id}. "
                    "Add it to TELEGRAM_ALLOWED_USER_IDS and restart the bot "
                    "to enable commands.",
                )
            return

        if user_id not in self.allowed_user_ids:
            self._send_message(chat_id, "You are not authorized to use this bot.")
            return

        try:
            if command == "help":
                self._send_message(
                    chat_id,
                    "/fetch - Fetch current matches and odds\n"
                    "/scan - Find arbitrage opportunities\n"
                    "/save - Save the last scan results to CSV\n"
                    "Send a betting screenshot - Read visible text and odds\n"
                    "/help - Show available commands",
                )
            elif command == "fetch":
                matches = self.scraper.fetch_matches()
                if matches:
                    self._send_message(chat_id, f"Fetched {len(matches)} matches.")
                else:
                    self._send_message(
                        chat_id,
                        "No match odds were parsed. OddsPortal may have no listed "
                        "fixtures or its page layout may have changed.",
                    )
            elif command == "scan":
                self.opportunities = self.scraper.scan_arbitrage()
                if not self.scraper.matches:
                    self._send_message(
                        chat_id, "No match odds are available to scan right now."
                    )
                else:
                    self._send_scan_results(chat_id)
            elif command == "save":
                if not self.opportunities:
                    self._send_message(chat_id, "No scan results to save.")
                else:
                    self.scraper.save_results(self.opportunities)
                    self._send_message(chat_id, "Scan results saved to the data directory.")
            else:
                self._send_message(chat_id, "Unknown command. Send /help for commands.")
        except Exception:
            self._send_message(
                chat_id, "That command failed. Check the bot logs and try again."
            )

    @staticmethod
    def _is_supported_image_document(message):
        document = message.get("document") or {}
        return document.get("mime_type") in {"image/jpeg", "image/png"}

    def _handle_screenshot(self, message, chat_id):
        photo_sizes = message.get("photo") or []
        if photo_sizes:
            image = max(photo_sizes, key=lambda item: item.get("file_size", 0))
        else:
            image = message["document"]

        try:
            recognized_text = self._read_image_text(image["file_id"])
        except (
            OSError,
            RuntimeError,
            requests.RequestException,
            subprocess.SubprocessError,
        ):
            self._send_message(
                chat_id,
                "I couldn't read that image. Try a clear screenshot with visible "
                "text and odds.",
            )
            return

        if not recognized_text:
            self._send_message(
                chat_id,
                "I couldn't detect readable text. Try a clearer screenshot with "
                "visible text and odds.",
            )
            return

        self._send_message(
            chat_id,
            "Text detected (please verify every team and number; OCR can be wrong):\n"
            + recognized_text,
        )

    def _read_image_text(self, file_id):
        file_info = self._api_request("getFile", {"file_id": file_id})
        file_path = file_info.get("file_path")
        if not file_path:
            raise RuntimeError("Telegram did not return an image path.")

        response = requests.get(
            f"{self.file_api_url}/{file_path}", timeout=(5, 30)
        )
        response.raise_for_status()
        if len(response.content) > 20 * 1024 * 1024:
            raise RuntimeError("Image exceeds Telegram's file size limit.")

        suffix = os.path.splitext(file_path)[1].lower()
        if suffix not in {".jpg", ".jpeg", ".png"}:
            suffix = ".img"

        with tempfile.NamedTemporaryFile(suffix=suffix) as image_file:
            image_file.write(response.content)
            image_file.flush()
            result = subprocess.run(
                ["tesseract", image_file.name, "stdout"],
                capture_output=True,
                text=True,
                timeout=20,
                check=True,
            )
        return result.stdout.strip()[:3200]

    def _send_scan_results(self, chat_id):
        if not self.opportunities:
            self._send_message(chat_id, "No arbitrage opportunities found.")
            return

        lines = [f"Found {len(self.opportunities)} arbitrage opportunity(ies):"]
        for opportunity in self.opportunities:
            lines.append(
                f"\n{opportunity['teams']}\n"
                f"Home {opportunity['home']:.2f} | "
                f"Draw {opportunity['draw']:.2f} | "
                f"Away {opportunity['away']:.2f}\n"
                f"Profit: {opportunity['profit_percent']:.2f}%"
            )

        message = "\n".join(lines)
        if len(message) > 4000:
            message = message[:3980] + "\n\nResults truncated."
        self._send_message(chat_id, message)

    def run(self):
        print("Telegram bot is running. Press Ctrl+C to stop.")
        offset = None
        while True:
            try:
                updates = self._api_request(
                    "getUpdates",
                    {"offset": offset, "timeout": 30},
                    timeout=40,
                )
                for update in updates:
                    offset = update["update_id"] + 1
                    try:
                        self._handle_update(update)
                    except RuntimeError:
                        print("Failed to send a Telegram response.")
            except KeyboardInterrupt:
                print("\nTelegram bot stopped.")
                return
            except RuntimeError:
                print("Telegram polling failed; retrying in 5 seconds.")
                time.sleep(5)
