import asyncio
import os

import structlog
from chancy import Chancy, Queue, QueuedJob, Worker, job

from .yt_dlp import download_video
from .post_processing import remove_silence, speed_up_audio

log: structlog.stdlib.BoundLogger = structlog.get_logger()

PREFERREDCODEC = "m4a"
DOWNLOAD_PATH = "/tmp"
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

chancy = Chancy(DB_URL)


@job(max_attempts=3)
def download_and_post_process(*, video_url: str, context: QueuedJob) -> None:
    log.info(f"`download_and_post_process` job started for task: {context.id}")
    download_video(video_url, DOWNLOAD_PATH, context.id, PREFERREDCODEC)

    audio_path = os.path.join(DOWNLOAD_PATH, context.id + "." + PREFERREDCODEC)

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
