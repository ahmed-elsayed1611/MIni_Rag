from fastapi import APIRouter, Depends  
from helpers import get_settings ,settings



base_router = APIRouter(
    prefix="/AI",
    tags=["AI Services"]
)


@base_router.get("/")
async def welcome(app_settings: settings = Depends(get_settings)):
    App_Name = app_settings.APP_NAME
    App_Version = app_settings.APP_VERSION
   
    return {"app_name": App_Name, "app_version": App_Version}