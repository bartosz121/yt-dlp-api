from dataclasses import dataclass

from chancy.job import QueuedJob
from litestar import Controller, post

from yt_dlp_api.worker import chancy, download


@dataclass
class ScheduleDownloadRequest:
    url: str


@dataclass
class ScheduleDownloadResponse:
    job_id: str


@dataclass
class JobStateResponse:
    state: QueuedJob.State


class YtDlpController(Controller):
    path = "/yt-dlp"

    @post("/schedule/download")
    async def schedule_download(
        self, data: ScheduleDownloadRequest
    ) -> ScheduleDownloadResponse:
        job = await chancy.push(download.job.with_kwargs(video_url=data.url))
        return ScheduleDownloadResponse(job.identifier)
