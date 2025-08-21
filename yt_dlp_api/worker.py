import asyncio
import json

import structlog
from chancy import (  # pyright: ignore[reportMissingTypeStubs]
    Chancy,
    Queue,
    QueuedJob,
    Worker,
    job,  # pyright: ignore[reportUnknownVariableType]
)

from yt_dlp_api import utils
from yt_dlp_api.config import settings
from yt_dlp_api.post_processing import remove_silence, speed_up_audio
from yt_dlp_api.transcription import transcript_aai
from yt_dlp_api.yt_dlp import download_video

log: structlog.stdlib.BoundLogger = structlog.get_logger()

chancy = Chancy(settings.DB_URL)


@job(max_attempts=3)
def download_and_post_process(
    *,
    video_url: str,
    context: QueuedJob,
) -> None:
    log.info(f"`download_and_post_process` job started for task: {context.id}")
    download_video(
        video_url,
        settings.DOWNLOAD_PATH,
        context.id,
        settings.PREFERREDCODEC,
    )

    audio_path = utils.get_audio_file_path_for_job(context.id)

    remove_silence(audio_path, replace_file=True)
    speed_up_audio(audio_path, replace_file=True)


@job(max_attempts=3)
async def transcription_assembly_ai(
    *,
    download_job_id: str,
    context: QueuedJob,
) -> None:
    audio_file_path = utils.get_audio_file_path_for_job(download_job_id)
    aai_client = utils.get_assembly_ai_client()
    transcription = await transcript_aai(aai_client, audio_file_path)

    transcription_file_path = utils.get_transcription_file_path_for_job(download_job_id)

    with open(transcription_file_path, "w") as f:
        json.dump(transcription, f, indent=4)

    log.info(f"Transcription of {audio_file_path} saved to {transcription_file_path}")


async def main():
    async with chancy:
        await chancy.migrate()
        await chancy.declare(Queue("default"))

        async with Worker(chancy) as worker:
            await worker.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
