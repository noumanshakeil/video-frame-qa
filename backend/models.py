from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class VideoJob(Base):
    __tablename__ = "video_jobs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    source_uri: Mapped[str] = mapped_column(String(240), default="")
    status: Mapped[str] = mapped_column(String(24), index=True, default="queued")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class VideoFrame(Base):
    __tablename__ = "video_frames"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(32), index=True)
    frame_index: Mapped[int] = mapped_column(Integer, default=0)
    timestamp_ms: Mapped[int] = mapped_column(Integer, default=0)
    caption: Mapped[str] = mapped_column(Text, default="")
    meta_json: Mapped[str] = mapped_column(Text, default="{}")

class FrameQuestion(Base):
    __tablename__ = "frame_questions"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(32), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
