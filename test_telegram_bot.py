import unittest
from unittest.mock import Mock, patch

import requests

from telegram_bot import TelegramBot


class TelegramScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.bot = TelegramBot("test-token", {123})

    def test_sends_ocr_text_for_authorized_photo(self):
        message = {
            "from": {"id": 123},
            "chat": {"id": 456},
            "photo": [
                {"file_id": "small"},
                {"file_id": "large", "file_size": 200},
            ],
        }

        with (
            patch.object(
                self.bot, "_read_image_text", return_value="Team A 2.10"
            ) as read_image,
            patch.object(self.bot, "_send_message") as send_message,
        ):
            self.bot._handle_update({"message": message})

        read_image.assert_called_once_with("large")
        send_message.assert_called_once_with(
            456,
            "Text detected (please verify every team and number; OCR can be wrong):\n"
            "Team A 2.10",
        )

    def test_rejects_unauthorized_photo(self):
        message = {
            "from": {"id": 999},
            "chat": {"id": 456},
            "photo": [{"file_id": "photo"}],
        }

        with (
            patch.object(self.bot, "_read_image_text") as read_image,
            patch.object(self.bot, "_send_message") as send_message,
        ):
            self.bot._handle_update({"message": message})

        read_image.assert_not_called()
        send_message.assert_called_once_with(
            456, "You are not authorized to use this bot."
        )

    def test_downloads_image_and_runs_tesseract(self):
        self.bot._api_request = Mock(return_value={"file_path": "photos/image.jpg"})
        response = Mock()
        response.content = b"image bytes"
        with (
            patch("telegram_bot.requests.get", return_value=response) as get_image,
            patch(
                "telegram_bot.subprocess.run",
                return_value=Mock(stdout="Team A 2.10\n"),
            ) as run_ocr,
        ):
            text = self.bot._read_image_text("photo-id")

        self.assertEqual(text, "Team A 2.10")
        self.bot._api_request.assert_called_once_with(
            "getFile", {"file_id": "photo-id"}
        )
        get_image.assert_called_once_with(
            "https://api.telegram.org/file/bottest-token/photos/image.jpg",
            timeout=(5, 30),
        )
        self.assertEqual(run_ocr.call_args.args[0][0], "tesseract")
        self.assertEqual(run_ocr.call_args.kwargs["timeout"], 20)

    def test_reports_download_failure_without_crashing(self):
        message = {
            "from": {"id": 123},
            "chat": {"id": 456},
            "photo": [{"file_id": "photo"}],
        }

        with (
            patch.object(
                self.bot,
                "_read_image_text",
                side_effect=requests.RequestException("download failed"),
            ),
            patch.object(self.bot, "_send_message") as send_message,
        ):
            self.bot._handle_update({"message": message})

        self.assertIn("couldn't read", send_message.call_args.args[1].lower())


if __name__ == "__main__":
    unittest.main()
