from dataclasses import dataclass
from typing import Annotated

from chancy.job import QueuedJob, Reference
from litestar import Controller, MediaType, Response, get, post
from litestar.exceptions import HTTPException
from litestar.params import Dependency, Parameter

from yt_dlp_api.worker import chancy, download


@dataclass
class ScheduleDownloadRequest:
    url: str


@dataclass
class ScheduleDownloadResponse:
    task_id: str


class YtDlpController(Controller):
    path = "/yt-dlp"

    @post("/job/download/schedule")
    async def schedule_download(
        self, data: ScheduleDownloadRequest
    ) -> ScheduleDownloadResponse:
        job = await chancy.push(download.job.with_kwargs(video_url=data.url))
        return ScheduleDownloadResponse(job.identifier)

    @get("/job/{job_id:str}/state")
    async def get_job_state(
        self, job_id: Annotated[str, Parameter(title="Job ID")]
    ) -> dict[str, QueuedJob.State]:
        ref = Reference(job_id)
        job = await chancy.get_job(ref)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"state": job.state}
