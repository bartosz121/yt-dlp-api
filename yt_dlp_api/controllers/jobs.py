from dataclasses import dataclass
from typing import Annotated

from chancy.job import QueuedJob, Reference
from litestar import Controller, get
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from yt_dlp_api.worker import chancy


@dataclass
class JobStateResponse:
    state: QueuedJob.State


class JobsController(Controller):
    path = "/jobs"

    @get("/{job_id:str}/state")
    async def get_job_state(
        self, job_id: Annotated[str, Parameter(title="Job ID")]
    ) -> JobStateResponse:
        ref = Reference(job_id)
        job = await chancy.get_job(ref)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobStateResponse(job.state)
