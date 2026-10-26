import os
from datetime import datetime
from typing import List, Dict, Any, Optional, AsyncIterator
from dotenv import load_dotenv
from sqlalchemy import String, Text, DateTime, ForeignKey, func, or_, select, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    thread_id: Mapped[str] = mapped_column(String(128), primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    tickers: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    telemetry: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "ALTER TABLE research_sessions "
                "ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"
            )
        )
        await conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_research_sessions_user_id "
                "ON research_sessions (user_id)"
            )
        )

async def close_db() -> None:
    await engine.dispose()

async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

async def session_thread_id_conflicts(thread_id: str, user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        stmt = select(ResearchSession.thread_id).where(
            ResearchSession.thread_id == thread_id,
            or_(
                ResearchSession.user_id.is_(None),
                ResearchSession.user_id != user_id,
            ),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

async def save_session(
    user_id: int,
    thread_id: str, 
    title: str, 
    query: str, 
    tickers: List[str], 
    report: Dict[str, Any], 
    telemetry: Dict[str, Any]
) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            stmt = select(ResearchSession).where(
                ResearchSession.thread_id == thread_id,
                ResearchSession.user_id == user_id,
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.title = title
                existing.query = query
                existing.tickers = tickers
                existing.report = report
                existing.telemetry = telemetry
            else:
                new_session = ResearchSession(
                    thread_id=thread_id,
                    user_id=user_id,
                    title=title,
                    query=query,
                    tickers=tickers,
                    report=report,
                    telemetry=telemetry
                )
                session.add(new_session)

async def get_all_sessions(user_id: int) -> List[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                ResearchSession.thread_id,
                ResearchSession.title,
                ResearchSession.query,
                ResearchSession.created_at
            )
            .where(ResearchSession.user_id == user_id)
            .order_by(ResearchSession.created_at.desc())
            .limit(50)
        )
        result = await session.execute(stmt)
        rows = result.all()
        return [
            {
                "thread_id": r.thread_id,
                "title": r.title,
                "query": r.query,
                "timestamp": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "Recent"
            }
            for r in rows
        ]

async def get_session_by_id(thread_id: str, user_id: int) -> Optional[Dict[str, Any]]:
    async with AsyncSessionLocal() as session:
        stmt = select(ResearchSession).where(
            ResearchSession.thread_id == thread_id,
            ResearchSession.user_id == user_id,
        )
        result = await session.execute(stmt)
        s = result.scalar_one_or_none()
        if not s:
            return None
        return {
            "thread_id": s.thread_id,
            "title": s.title,
            "query": s.query,
            "report": s.report,
            "telemetry": s.telemetry,
            "timestamp": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "Recent"
        }