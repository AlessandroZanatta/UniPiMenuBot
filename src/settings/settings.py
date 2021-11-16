from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    # Bot token
    bot_api_key: str = Field(..., env="bot_api_key")
    restaurants: List[str] = ["cammeo", "martiri", "praticelli", "rosellini", "betti"]
    menus_dir: str = "/menus"

    # Redis keys
    redis_users: str = "users"
    redis_active_users: str = "active_users"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
