from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import video_qa as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    jobs = await svc.list_jobs(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Video Frame QA", "jobs": jobs, "answer": None})

@router.post("/ui/jobs")
async def ui_job(request: Request, title: str = Form(...), transcript: str = Form(...), db: AsyncSession = Depends(get_db)):
    job = await svc.create_job(db, title, "file://local.mp4", transcript)
    ans = await svc.ask(db, job.id, "What happens in the video?")
    jobs = await svc.list_jobs(db)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Video Frame QA", "jobs": jobs, "answer": ans.answer},
    )
