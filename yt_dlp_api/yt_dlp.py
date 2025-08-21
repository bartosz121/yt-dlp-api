import structlog
import yt_dlp

log: structlog.stdlib.BoundLogger = structlog.get_logger()


def download_video(url: str, path: str, filename: str, preferred_codec: str) -> None:
    log.info(f"Downloading audio for {url!s}")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{path}/{filename}.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": preferred_codec,
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    log.info(f"Downloaded audio for {url!s}")
