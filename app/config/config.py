from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # База данных
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    # JWT
    #надо добавить так как .env ругается
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str

    @property 
    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def get_jwt_key(self) -> str:
        return self.JWT_SECRET_KEY
    
settings = Settings()