from fastapi import FastAPI
from mangum import Mangum
from app.api.v1 import weather

app = FastAPI(
    title="Weather API",
    description="Weather Data Collection and Notification API",
    version="1.0.0",
)

app.include_router(weather.router, prefix="/api/v1/weather", tags=["weather"])

# Handler for AWS Lambda
handler = Mangum(app)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
