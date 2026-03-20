FROM public.ecr.aws/lambda/python:3.10

WORKDIR /var/task

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY static/ ./static/

RUN mkdir -p session_logs
RUN mkdir -p faiss_index
RUN mkdir -p chroma_db

EXPOSE 8000

# Start server
CMD ["src.api.main.handler"]