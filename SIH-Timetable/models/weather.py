from enum import Enum
from pydantic import BaseModel
from typing import Optional

class WeatherStatus(Enum):
    NORMAL = "normal"
    RAIN = "rain"
    EXTREME_HEAT = "extreme_heat"
    STORM = "storm"

class WeatherData(BaseModel):
    status: WeatherStatus
    temperature: float
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None
