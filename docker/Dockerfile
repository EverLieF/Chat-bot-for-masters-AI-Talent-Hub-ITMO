FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential poppler-utils && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["bash", "-lc", "python -m app.ingest && python -m app.search.index && python -m app.webapi"]