from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENWEATHER_API_KEY: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str = "us-east-1"
    DYNAMODB_ENDPOINT_URL: str = "http://localhost:4566"
    SNS_ENDPOINT_URL: str = "http://localhost:4566"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


# Create a single instance of Settings to be imported by other modules
settings = Settings()
