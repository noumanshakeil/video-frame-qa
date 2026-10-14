import pytest

@pytest.mark.asyncio
async def test_video_ask(client):
    j = await client.post("/api/jobs", json={"title": "Standup", "transcript": "Alice opens laptop. Bob shares screen."})
    jid = j.json()["id"]
    fr = await client.get(f"/api/jobs/{jid}/frames")
    assert len(fr.json()["frames"]) >= 1
    a = await client.post(f"/api/jobs/{jid}/ask", json={"question": "Who shares screen?"})
    assert a.status_code == 200
    assert a.json()["answer"]
