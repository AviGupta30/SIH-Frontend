from fastapi import APIRouter, HTTPException
from models.weather import WeatherData
from services.weather_service import WeatherService, WeatherBasedScheduler

router = APIRouter(prefix="/weather", tags=["weather"])
weather_service = WeatherService()
scheduler = WeatherBasedScheduler(weather_service)

@router.get("/status", response_model=WeatherData)
async def get_weather_status():
    """Get current weather status and conditions"""
    return await weather_service.check_weather()

@router.get("/impact")
async def get_weather_impact():
    """Get weather impact on current schedule"""
    weather_data = await weather_service.check_weather()
    # Implementation of impact assessment
    return {"status": weather_data.status, "impact": "medium"}
