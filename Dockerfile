FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "cse476.serving:make_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
