from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="R & A Agent API",
    description="Backend API for the Research & Answer Agent system.",
    version="0.1.0",
)

# Enable CORS for local development with Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint to verify that the service is running."""
    return {"status": "ok", "app": "R & A Agent"}
