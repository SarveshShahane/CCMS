from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    def __init__(self):
        self.postgre_user: str = os.getenv("POSTGRE_USER")
        self.postgre_password: str = os.getenv("POSTGRE_PASSWORD")
        self.postgre_db: str = os.getenv("POSTGRE_DB")
        self.postgre_host: str = os.getenv("POSTGRE_HOST")
        self.postgre_port: int = int(os.getenv("POSTGRE_PORT"))
        self.postgres_url: str = os.getenv(
            "POSTGRES_URL",
            f"postgresql+asyncpg://{self.postgre_user}:{self.postgre_password}@{self.postgre_host}:{self.postgre_port}/{self.postgre_db}",
        )
        
        self.redis_host: str = os.getenv("REDIS_HOST", "127.0.0.1")
        self.redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_url: str = os.getenv(
            "REDIS_URL",
            f"redis://{self.redis_host}:{self.redis_port}",
        )

        self.groq_api_key: str = os.getenv("GROQ_API_KEY")
        self.llm_model: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        self.llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.llm_max_tokens: int | None = (
            int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None
        )



settings = Settings()

