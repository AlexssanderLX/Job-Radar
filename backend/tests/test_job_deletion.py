from datetime import datetime, timezone

import pytest

from app.models.job import Job


async def add_job(db_session, suffix: str = "1"):
    job = Job(
        title=f"Test Job {suffix}", company="Acme", source="test",
        url=f"https://example.com/jobs/{suffix}", apply_url=f"https://example.com/jobs/{suffix}",
        collected_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.mark.asyncio
async def test_delete_individual_job(client, db_session):
    job = await add_job(db_session)
    assert (await client.delete(f"/api/jobs/{job.id}")).status_code == 204
    assert (await client.get(f"/api/jobs/{job.id}")).status_code == 404


@pytest.mark.asyncio
async def test_clear_all_jobs_preserves_access_history(client, db_session):
    job = await add_job(db_session)
    await add_job(db_session, "2")
    await client.post(f"/api/jobs/{job.id}/access")
    assert (await client.delete("/api/jobs")).status_code == 204
    assert (await client.get("/api/jobs")).json() == []
    accesses = (await client.get("/api/link-accesses")).json()
    assert accesses["total"] == 1
    assert accesses["items"][0]["job_id"] is None
