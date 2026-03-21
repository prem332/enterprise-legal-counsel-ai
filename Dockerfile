FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
ENV XDG_CACHE_HOME=/app/models

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY src/ ./src/
COPY static/ ./static/

EXPOSE 8000

# Start server
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]