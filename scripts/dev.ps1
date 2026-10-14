# Dev server for video-frame-qa
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
