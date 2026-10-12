FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py scraper.py storage.py telegram_bot.py ./
COPY web_app.py ./
COPY web/ ./web/

CMD ["python", "main.py", "--telegram"]
