from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    WEATHER_API_KEY: str = "YOUR_API_KEY"
    WEATHER_THRESHOLD = {
        "rain": 25,  # mm of rain
        "temperature": 40,  # Celsius
        "wind": 70,  # km/h
    }
    
    class Config:
        env_file = ".env"

settings = Settings()
