# -*- coding: utf-8 -*-
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Locations(BaseModel):
    base: str = "{root}/var"
    logs: str = "{root}/var/logs"
    temp: str = "{root}/var/temp"
    static: str = "{root}/app/static"
    templates: str = "{root}/app/templates"


class Logging(BaseModel):
    level: str = "INFO"
    format: str = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> "
                   "| <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


class Settings(BaseSettings, extra="allow"):
    logging: Logging
