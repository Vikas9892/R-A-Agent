import logging
import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.chat import router as chat_router

# Configure standard structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("app.api")

app = FastAPI(
    title="R & A Agent API",
    description="Backend API for the Research & Answer Agent system.",
    version="0.1.0",
)

# Request ID and observability middleware
@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.time()

    logger.info("[%s] Request received: %s %s", request_id, request.method, request.url.path)

    try:
        response: Response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "[%s] Request completed: %s (status=%d, latency=%.2fms)",
            request_id,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "[%s] Request error on %s: %s (latency=%.2fms)",
            request_id,
            request.url.path,
            exc,
            duration_ms,
        )
        raise

# Enable CORS for local development with Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(chat_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Health check endpoint to verify that the service is running."""
    return {"status": "ok", "app": "R & A Agent"}
