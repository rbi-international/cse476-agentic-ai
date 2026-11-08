# The PR Review Crew web service. Build from this folder:
#   docker build -t pr-review-crew .
#   docker run -p 8080:8080 -e GROQ_API_KEY=... pr-review-crew
# Cloud Run and ECS set PORT; the default is 8080.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY crew ./crew
COPY demo_repo ./demo_repo
COPY samples ./samples
RUN useradd --create-home --uid 1000 agent && chown -R agent /app
USER agent
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8080')+'/health')"
CMD ["sh", "-c", "uvicorn crew.web:app --host 0.0.0.0 --port ${PORT:-8080}"]
