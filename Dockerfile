FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /tmp/downloads /app/logs /app/storage \
    && chown -R appuser:appuser /app /tmp/downloads

USER appuser

EXPOSE 8080

CMD ["python", "bot.py"]
