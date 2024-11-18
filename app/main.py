from fastapi import FastAPI
from mangum import Mangum
from app.api.v1 import weather
from app.middleware.logging_middleware import logging_middleware
from app.middleware.error_middleware import error_handling_middleware
from app.middleware.performance_middleware import performance_middleware

app = FastAPI(
    title="Weather API",
    description="Weather Data Collection and Notification API",
    version="1.0.0",
)

# Add middleware in the desired order
app.middleware("http")(error_handling_middleware)
app.middleware("http")(logging_middleware)
app.middleware("http")(performance_middleware)

app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])

# Handler for AWS Lambda
handler = Mangum(app)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}