from __future__ import annotations
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import FrameQuestion, VideoFrame, VideoJob
from backend.services.rag_core import Hit, pack_citations, score_chunk
from backend.utils.ids import short_id
from backend.vision.caption_idx import caption_overlap

async def create_job(session: AsyncSession, title: str, source_uri: str, transcript: str) -> VideoJob:
    job = VideoJob(id=short_id(), title=title.strip()[:160], source_uri=source_uri.strip()[:240], status="queued")
    session.add(job)
    await session.flush()
    lines = [ln.strip() for ln in (transcript or "").split(".") if ln.strip()]
    for i, ln in enumerate(lines[:12]):
        session.add(
            VideoFrame(
                id=short_id(),
                job_id=job.id,
                frame_index=i,
                timestamp_ms=i * 1000,
                caption=ln,
                meta_json=json.dumps({"sampled": True, "width": 1280, "height": 720}),
            )
        )
    job.status = "sampled"
    await session.commit()
    await session.refresh(job)
    return job

async def list_jobs(session: AsyncSession) -> list[VideoJob]:
    return list((await session.execute(select(VideoJob).order_by(VideoJob.created_at.desc()))).scalars())

async def frames_for(session: AsyncSession, job_id: str) -> list[VideoFrame]:
    stmt = select(VideoFrame).where(VideoFrame.job_id == job_id).order_by(VideoFrame.frame_index)
    return list((await session.execute(stmt)).scalars())

async def ask(session: AsyncSession, job_id: str, question: str) -> FrameQuestion:
    frames = await frames_for(session, job_id)
    hits: list[Hit] = []
    for fr in frames:
        s = max(score_chunk(question, fr.caption), caption_overlap(question, fr.caption))
        if s <= 0:
            continue
        hits.append(
            Hit(
                chunk_id=fr.id,
                document_id=job_id,
                title=f"frame {fr.frame_index}",
                text=fr.caption,
                score=s,
                meta={"timestamp_ms": fr.timestamp_ms},
            )
        )
    hits.sort(key=lambda h: h.score, reverse=True)
    hits = hits[:5]
    context = pack_citations(hits) if hits else "(no frames)"
    llm = get_llm()
    answer = await llm.complete(
        f"Video frame QA. Question: {question}\n\nFRAMES:\n{context}",
        system="Answer using frame captions only; cite frame indices.",
    )
    row = FrameQuestion(id=short_id(), job_id=job_id, question=question.strip(), answer=answer)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row
