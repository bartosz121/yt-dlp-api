import asyncio
import os

import structlog
from chancy import Chancy, Queue, QueuedJob, Worker, job

from yt_dlp_api.config import settings
from yt_dlp_api.post_processing import remove_silence, speed_up_audio
from yt_dlp_api.utils import get_audio_path_for_job
from yt_dlp_api.yt_dlp import download_video

log: structlog.stdlib.BoundLogger = structlog.get_logger()

chancy = Chancy(settings.DB_URL)


@job(max_attempts=3)
def download_and_post_process(*, video_url: str, context: QueuedJob) -> None:
    log.info(f"`download_and_post_process` job started for task: {context.id}")
    download_video(
        video_url,
        settings.DOWNLOAD_PATH,
        context.id,
        settings.PREFERREDCODEC,
    )

    audio_path = get_audio_path_for_job(context.id)

    remove_silence(audio_path, replace_file=True)
    speed_up_audio(audio_path, replace_file=True)


@job(max_attempts=3)
async def transcribe_assembly_ai():
    pass


@job(max_attempts=1)
def transcribe_local():
    pass


async def main():
    async with chancy:
        await chancy.migrate()
        await chancy.declare(Queue("default"))

        async with Worker(chancy) as worker:
            await worker.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
