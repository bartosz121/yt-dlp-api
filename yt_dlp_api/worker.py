import asyncio
import os

import structlog
import yt_dlp
from chancy import Chancy, Queue, QueuedJob, Worker, job

log: structlog.stdlib.BoundLogger = structlog.get_logger()

DOWNLOAD_PATH = "/tmp"
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

chancy = Chancy(DB_URL)


@job(max_attempts=3)
def download(*, video_url: str, context: QueuedJob):
    log.info(f"Download started for task: {context.id}")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_PATH}/{context.id}.opus",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "opus",
                "preferredquality": "96",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


async def main():
    async with chancy:
        await chancy.migrate()
        await chancy.declare(Queue("default"))

        async with Worker(chancy) as worker:
            await worker.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
