FROM python:3.12-slim
WORKDIR /app
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt
COPY src ./src
ENV PYTHONPATH=/app/src
RUN useradd --create-home --uid 1000 agent
USER agent
EXPOSE 8000
CMD ["uvicorn", "cse476.live:make_live_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
