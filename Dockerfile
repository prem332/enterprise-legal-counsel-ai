FROM python:3.10-slim

WORKDIR /app

# Copy requirements first (Docker caching!)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY static/ ./static/

# Create necessary folders
RUN mkdir -p session_logs
RUN mkdir -p faiss_index
RUN mkdir -p chroma_db

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]