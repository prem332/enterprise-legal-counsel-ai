FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY static/ ./static/

ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV HF_HOME=/tmp/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers
ENV XDG_CACHE_HOME=/tmp/cache

EXPOSE 8000

# Start server
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]