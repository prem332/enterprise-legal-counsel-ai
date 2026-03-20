FROM python:3.10-slim

WORKDIR /app

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.7.1 /lambda-adapter /opt/extensions/lambda-adapter

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY static/ ./static/

RUN mkdir -p session_logs
RUN mkdir -p faiss_index
RUN mkdir -p chroma_db

EXPOSE 8000
ENV PORT=8000
ENV AWS_LWA_PORT=8000

# Start server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]