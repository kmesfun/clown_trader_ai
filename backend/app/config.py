from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://clown:honkhonk@localhost:5432/clown_arena"
    polygon_api_key: str = ""
    alpha_vantage_key: str = ""
    anthropic_api_key: str = ""
    environment: str = "development"

    starting_cash: float = 100_000.0
    slippage_pct: float = 0.0005  # 0.05%
    borrow_rate_daily: float = 0.0002  # 0.02% per day for shorts
    pdt_day_trade_limit: int = 3
    pdt_min_equity: float = 25_000.0
    pdt_lockout_days: int = 90
    max_position_pct: float = 0.25  # 25% max single position


settings = Settings()
