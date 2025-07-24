from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class BotConfig(BaseModel):
    token: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template",".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        
    )
    bot_token: BotConfig
    
settings = Settings()
