from fastapi import FastAPI
from app.services.rate_limit import attach_rate_limit
from app.api.endpoints.process import router as process_router

app = FastAPI(
    title="Productivity Rule Engine + LLM",
    version="1.0.0",
    description="Hybrid rules + LLM productivity analysis engine"
)

# Attach rate limiting middleware & handler
attach_rate_limit(app)

# Include API routes
app.include_router(process_router)

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    Returns service status.
    """
    return {"status": "healthy"}
