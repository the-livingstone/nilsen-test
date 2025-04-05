from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    host: str = '0.0.0.0'
    port: int = 8000
    title: str = 'LRU Cache с TTL'
    cache_size: int = 10
    logging_level: str = 'INFO'

    debug: bool = True
    
    
    model_config = SettingsConfigDict(
        env_file=".env",
    )

settings = AppSettings()