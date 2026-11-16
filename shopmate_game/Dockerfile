# Hack ShopMate, the Unit VI class game. Build from this folder:
#   docker build -t shopmate-game .
#   docker run --rm -p 8090:8080 -e GROQ_API_KEY shopmate-game
# Cloud Run sets PORT; the default is 8080.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY game ./game
RUN useradd --create-home --uid 1000 player && chown -R player /app
USER player
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8080')+'/health')"
CMD ["sh", "-c", "uvicorn game.web:app --host 0.0.0.0 --port ${PORT:-8080}"]
