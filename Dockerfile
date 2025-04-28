FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /usr/local/nltk_data && \
    python -m nltk.downloader -d /usr/local/nltk_data wordnet omw-1.4
ENV NLTK_DATA=/usr/local/nltk_data

COPY . .

RUN mkdir -p tmp static/results

EXPOSE 5000

ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

CMD ["gunicorn", "--bind=0.0.0.0:5000", "--timeout=600", "app:app"]

