FROM python:3.11-slim

# Prevent Python from creating .pyc files and enable real-time logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system appuser \
    && adduser --system --home /app --ingroup appuser appuser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .
RUN chmod +x /app/scripts/start.sh

USER appuser

EXPOSE 8000

CMD ["/app/scripts/start.sh"]
