FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
COPY n8n/ n8n/
COPY data/ data/
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/health')" || exit 1
CMD ["python3", "n8n/webhook_adapter.py"]
