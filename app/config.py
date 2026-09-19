import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET: str = "carecircle-data"
    BEDROCK_MODEL_ID: str = "amazon.nova-lite-v1:0"
    FRONTEND_URL: str = "http://localhost:3000"
    USE_LAMBDA_AI: bool = False
    CARE_AI_LAMBDA_NAME: str = "carecircle-ai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
