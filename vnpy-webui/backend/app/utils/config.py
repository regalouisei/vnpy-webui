# 配置

import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置"""
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database/vnpy.db")

    # VnPy 配置
    VNPY_SETTING_PATH: str = os.getenv("VNPY_SETTING_PATH", "~/.vntrader/vt_setting.json")

    # CTP 配置
    CTP_USERNAME: str = os.getenv("CTP_USERNAME", "17130")
    CTP_PASSWORD: str = os.getenv("CTP_PASSWORD", "123456")
    CTP_BROKERID: str = os.getenv("CTP_BROKERID", "9999")
    CTP_TD_ADDRESS: str = os.getenv("CTP_TD_ADDRESS", "tcp://trading.openctp.cn:30001")
    CTP_MD_ADDRESS: str = os.getenv("CTP_MD_ADDRESS", "tcp://trading.openctp.cn:30011")

    # WebSocket 配置
    WS_HOST: str = os.getenv("WS_HOST", "0.0.0.0")
    WS_PORT: int = int(os.getenv("WS_PORT", "8000"))

    # API 配置
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "vnpy-webui"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """获取配置"""
    return Settings()

settings = get_settings()
