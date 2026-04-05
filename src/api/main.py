from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from mangum import Mangum
from fastapi.responses import FileResponse
from src.api.routes import chat, documents, logs
from src.security.rate_limiter import limiter
import os

app = FastAPI(
    title="Enterprise Legal Counsel AI",
    description="Production grade Indian Legal AI Assistant powered by Multi-Agent RAG, LLaMA 3 and LangChain",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)
app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)
app.include_router(
    logs.router,
    prefix="/api/v1/logs",
    tags=["Logs"]
)

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")


if os.path.exists("static"):
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static"
    )

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise Legal Counsel AI",
        "version": "1.0.0"
    }

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found"}
    )

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again."}
    )

handler = Mangum(app, lifespan="off")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)