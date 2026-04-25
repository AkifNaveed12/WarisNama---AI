import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "WarisNama AI Backend"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Path to the root of the existing project (where core/, ai/, docs/ live)
    # Assuming backend/ is inside the same root
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    CORE_DIR: Path = BASE_DIR / "core"
    AI_DIR: Path = BASE_DIR / "ai"
    DOCS_DIR: Path = BASE_DIR / "docs"

    # Add to sys.path automatically in main.py
    @property
    def pythonpath(self):
        return str(self.BASE_DIR)

settings = Settings()
