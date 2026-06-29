from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432 #fail fast
    DB_NAME: str = "task_manager" #fail fast
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    SECRET_KEY: str = "super-secret-key-change-me"

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# TODO:
# remove hard coded secrets.
# Добавить интерфейсы на репозитории.
# Добавить DI Container Dishka => сделать рефактор. 
# Пообщаться с Чатом ГПТ, может стоит выносить сессию вне репозиториев в сервисный слой.
