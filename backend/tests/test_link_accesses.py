from datetime import datetime, timezone

import pytest

from app.models.job import Job


async def create_job(db_session):
    job = Job(
        title="Backend Developer", company="Acme", source="gupy",
        url="https://acme.gupy.io/jobs/123", apply_url="https://acme.gupy.io/jobs/123",
        collected_at=datetime.now(timezone.utc),
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    return job


@pytest.mark.asyncio
async def test_records_and_increments_normalized_access(client, db_session):
    job = await create_job(db_session)
    first = await client.post("/api/link-accesses", json={
        "url": "https://acme.gupy.io/jobs/123?utm_source=test", "job_id": job.id,
        "title": job.title, "company": job.company, "source": job.source,
    })
    assert first.status_code == 201
    second = await client.post("/api/jobs/%s/access" % job.id)
    assert second.status_code == 201
    assert second.json()["access_count"] == 2
    jobs = await client.get("/api/jobs")
    saved = jobs.json()[0]
    assert saved["access_count"] == 2
    assert saved["has_been_accessed"] is True


@pytest.mark.asyncio
async def test_lists_filters_and_deletes_without_deleting_job(client, db_session):
    job = await create_job(db_session)
    created = await client.post("/api/jobs/%s/access" % job.id)
    response = await client.get("/api/link-accesses", params={"source": "gupy"})
    assert response.status_code == 200
    assert response.json()["total"] == 1
    access_id = created.json()["id"]
    assert (await client.delete(f"/api/link-accesses/{access_id}")).status_code == 204
    assert (await client.get(f"/api/jobs/{job.id}")).status_code == 200


@pytest.mark.asyncio
async def test_rejects_non_http_url(client):
    response = await client.post("/api/link-accesses", json={"url": "javascript:alert(1)"})
    assert response.status_code == 422
