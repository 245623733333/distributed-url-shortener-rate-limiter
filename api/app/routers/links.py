from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import ClickEvent, ShortLink
from app.schemas import AnalyticsRead, LinkCreate, LinkListItem, LinkRead
from app.services.rate_limiter import rate_limiter
from app.services.shortener import generate_unique_code, is_expired

router = APIRouter(tags=["links"])


def short_url(code: str) -> str:
    return f"{get_settings().base_url.rstrip('/')}/{code}"


def serialize_link(link: ShortLink) -> LinkRead:
    return LinkRead(
        id=link.id,
        code=link.code,
        original_url=link.original_url,
        short_url=short_url(link.code),
        custom_alias=link.custom_alias,
        expires_at=link.expires_at,
        is_active=link.is_active,
        click_count=link.click_count,
        created_at=link.created_at,
    )


@router.post("/api/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, request: Request, db: Session = Depends(get_db)) -> LinkRead:
    rate_limiter.check(request)

    alias = payload.custom_alias
    if alias:
        existing = db.scalar(select(ShortLink).where((ShortLink.code == alias) | (ShortLink.custom_alias == alias)))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Custom alias is already taken.")

    link = ShortLink(
        code=alias or "pending",
        custom_alias=alias,
        original_url=str(payload.original_url),
        expires_at=payload.expires_at,
    )
    db.add(link)
    db.flush()
    if not alias:
        link.code = generate_unique_code(db, link.id)
    db.commit()
    db.refresh(link)
    return serialize_link(link)


@router.get("/api/links", response_model=list[LinkListItem])
def list_links(db: Session = Depends(get_db)) -> list[LinkListItem]:
    rows = db.scalars(select(ShortLink).order_by(desc(ShortLink.created_at)).limit(50)).all()
    return [
        LinkListItem(
            code=row.code,
            original_url=row.original_url,
            short_url=short_url(row.code),
            click_count=row.click_count,
            expires_at=row.expires_at,
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/api/links/{code}/analytics", response_model=AnalyticsRead)
def get_analytics(code: str, db: Session = Depends(get_db)) -> AnalyticsRead:
    link = db.scalar(select(ShortLink).where(ShortLink.code == code))
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found.")

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    clicks_last_24h = db.scalar(
        select(func.count(ClickEvent.id)).where(ClickEvent.link_id == link.id, ClickEvent.created_at >= since)
    ) or 0
    referrer_rows = db.execute(
        select(ClickEvent.referer, func.count(ClickEvent.id))
        .where(ClickEvent.link_id == link.id)
        .group_by(ClickEvent.referer)
        .order_by(desc(func.count(ClickEvent.id)))
        .limit(5)
    ).all()
    recent_rows = db.scalars(
        select(ClickEvent).where(ClickEvent.link_id == link.id).order_by(desc(ClickEvent.created_at)).limit(10)
    ).all()

    return AnalyticsRead(
        code=link.code,
        original_url=link.original_url,
        short_url=short_url(link.code),
        total_clicks=link.click_count,
        clicks_last_24h=clicks_last_24h,
        top_referrers=[{"referer": row[0] or "Direct", "clicks": row[1]} for row in referrer_rows],
        recent_clicks=[
            {
                "ip_address": row.ip_address,
                "referer": row.referer or "Direct",
                "country": row.country,
                "created_at": row.created_at.isoformat(),
            }
            for row in recent_rows
        ],
    )


@router.get("/{code}")
def redirect_link(code: str, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> RedirectResponse:
    link = db.scalar(select(ShortLink).where(ShortLink.code == code))
    if not link or not link.is_active or is_expired(link):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found or expired.")

    link.click_count += 1
    db.commit()
    background_tasks.add_task(record_click, link.id, request.client.host if request.client else "unknown", request.headers.get("user-agent", ""), request.headers.get("referer", ""))
    return RedirectResponse(link.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


def record_click(link_id: int, ip_address: str, user_agent: str, referer: str) -> None:
    from app.database import SessionLocal

    hostname = urlparse(referer).hostname or ""
    normalized_referer = hostname[:200]
    with SessionLocal() as db:
        db.add(
            ClickEvent(
                link_id=link_id,
                ip_address=ip_address[:64],
                user_agent=user_agent[:500],
                referer=normalized_referer,
            )
        )
        db.commit()
