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
        
        self.redis_host: str = os.getenv("REDIS_HOST")
        self.redis_port: int = int(os.getenv("REDIS_PORT"))
        self.redis_url: str = os.getenv(
            "REDIS_URL",
            f"redis://{self.redis_host}:{self.redis_port}",
        )


settings = Settings()

