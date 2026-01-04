from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path


class Settings(BaseSettings):

    load_dotenv()

    # API Configuration
    api_title: str = "ESG Analyzer API"
    api_description: str = "ESG Analyzer"
    api_version: str = "0.1.0"

    # LLM Configuration
    llm_api_key: Optional[str] = os.getenv("LLM_API_KEY")
    llm_model: str = "llama-3.1-8b-instant"
    llm_temperature: float = 0.0
    llm_max_output_tokens: int = 4096

    db_path: str = str(Path(__file__).parent.parent.parent / "ingestion" / "sqlite_db" / "advisor_esg_silver.db")

    model_config = {"env_file": ".env", "extra": "allow"}
