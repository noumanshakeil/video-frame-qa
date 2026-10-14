from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import video_qa as svc

class JobIn(BaseModel):
    title: str = Field(min_length=2)
    source_uri: str = ""
    transcript: str = Field(min_length=5)

class AskIn(BaseModel):
    question: str = Field(min_length=3)

router = APIRouter()

@router.post("/jobs")
async def create_job(payload: JobIn, db: AsyncSession = Depends(get_db)):
    job = await svc.create_job(db, payload.title, payload.source_uri, payload.transcript)
    return {"id": job.id, "status": job.status}

@router.get("/jobs")
async def jobs(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_jobs(db)
    return {"jobs": [{"id": j.id, "title": j.title, "status": j.status} for j in rows]}

@router.get("/jobs/{job_id}/frames")
async def frames(job_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.frames_for(db, job_id)
    import json
    return {
        "frames": [
            {
                "index": f.frame_index,
                "timestamp_ms": f.timestamp_ms,
                "caption": f.caption,
                "meta": json.loads(f.meta_json or "{}"),
            }
            for f in rows
        ]
    }

@router.post("/jobs/{job_id}/ask")
async def ask(job_id: str, payload: AskIn, db: AsyncSession = Depends(get_db)):
    row = await svc.ask(db, job_id, payload.question)
    return {"id": row.id, "answer": row.answer}
