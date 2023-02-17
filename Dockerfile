# Builder stage
FROM python:3.11.2-slim as builder

RUN apt-get update && \
    apt-get install -y musl-dev libpq-dev gcc && \
    python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Operational stage
FROM python:3.11.2-slim

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY . /app/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DASH_DEBUG_MODE=False

EXPOSE 8050
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "wsgi:serve"]