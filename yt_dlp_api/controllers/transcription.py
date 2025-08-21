from dataclasses import dataclass
from typing import Annotated, Any, cast

import anyio
from chancy.job import QueuedJob, Reference  # pyright: ignore[reportMissingTypeStubs]
from litestar import Controller, get, post
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from yt_dlp_api.utils import read_transcription_data_from_file
from yt_dlp_api.worker import chancy, transcription_assembly_ai


@dataclass
class ScheduleTranscribe:
    download_job_id: str


@dataclass
class ScheduleTranscribeResponse:
    job_id: str


@dataclass
class TranscriptionTextOnlyResponse:
    text: str


class TranscriptionController(Controller):
    path = "/transcript"

    @post("/schedule/transcript-aai")
    async def schedule_transcription_assembly_ai(
        self, data: ScheduleTranscribe
    ) -> ScheduleTranscribeResponse:
        job = await chancy.push(
            transcription_assembly_ai.job.with_kwargs(  # pyright: ignore[reportUnknownMemberType]
                download_job_id=data.download_job_id
            )
        )
        return ScheduleTranscribeResponse(job_id=job.identifier)

    @get("/{job_id:str}/text")
    async def get_transcription_text_only(
        self,
        job_id: Annotated[str, Parameter(title="Transcript job ID")],
    ) -> TranscriptionTextOnlyResponse:
        ref = Reference(job_id)
        job = await chancy.get_job(ref)
        if job is None:
            raise HTTPException(status_code=404, detail="Transcript job not found")

        if job.state != QueuedJob.State.SUCCEEDED:
            raise HTTPException(status_code=400, detail="Job not completed")

        transcript_job_kwargs = job.kwargs or {}
        download_job_id: str | None = transcript_job_kwargs.get("download_job_id")

        if download_job_id is None:
            raise HTTPException(
                status_code=500, detail="Download job id not found in transcript job kwargs"
            )

        transcription_data = cast(
            dict[str, Any],
            await anyio.to_thread.run_sync(  # type: ignore
                read_transcription_data_from_file, download_job_id
            ),
        )
        transcription_text = transcription_data["text"]

        return TranscriptionTextOnlyResponse(text=transcription_text)
