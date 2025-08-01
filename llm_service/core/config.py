from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class BotConfig(BaseModel):
    token: str
class YandexGpt(BaseModel):
    folder_id: str
    auth: str

class TelethonConfig(BaseModel):
    api_id: int
    api_hash:str
class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo:bool = False
    echo_pool: bool = False
    pool_size : int = 50
    max_overflow: int = 20
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template",".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        
    )
    db: DatabaseConfig
    bot_token: BotConfig
    telethon_set: TelethonConfig
    llm_set: YandexGpt    
settings = Settings()
