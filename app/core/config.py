from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int 
    DB_NAME: str 
    DB_USER: str
    DB_PASSWORD: str 

    SECRET_KEY: str 

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
