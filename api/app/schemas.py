from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = Field(default=None, min_length=3, max_length=32)
    expires_at: datetime | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Alias can only contain letters, numbers, hyphens, and underscores.")
        return value


class LinkRead(BaseModel):
    id: int
    code: str
    original_url: str
    short_url: str
    custom_alias: str | None
    expires_at: datetime | None
    is_active: bool
    click_count: int
    created_at: datetime


class LinkListItem(BaseModel):
    code: str
    original_url: str
    short_url: str
    click_count: int
    expires_at: datetime | None
    created_at: datetime


class AnalyticsRead(BaseModel):
    code: str
    original_url: str
    short_url: str
    total_clicks: int
    clicks_last_24h: int
    top_referrers: list[dict[str, int | str]]
    recent_clicks: list[dict[str, str]]
