from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    
    APP_NAME: str = "Intent-Based Firewall"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    RATE_LIMIT_REQUESTS: int = 100  
    RATE_LIMIT_WINDOW: int = 60     
    
    VDF_ENABLED: bool = True
    VDF_TIME_PARAMETER: int = 500000      
    VDF_TIMEOUT: int = 120           
    
    MEMORY_HARD_ENABLED: bool = True
    MEMORY_COST: int = 65536    
    TIME_COST: int = 3          
    PARALLELISM: int = 4        
    
    CHAP_ENABLED: bool = True
    CHAP_TIMEOUT: int = 60
    
    SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/firewall.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def print_config():
    print("\n" + "="*50)
    print("CONFIGURATION")
    print("="*50)
    print(f"App Name: {settings.APP_NAME}")
    print(f"Version: {settings.APP_VERSION}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"Rate Limit: {settings.RATE_LIMIT_REQUESTS} req/{settings.RATE_LIMIT_WINDOW}s")
    print(f"VDF Enabled: {settings.VDF_ENABLED}")
    print(f"Memory-Hard Enabled: {settings.MEMORY_HARD_ENABLED}")
    print("="*50 + "\n")

if __name__ == "__main__":
    print_config()
