import os
from http import HTTPStatus

from yt_dlp_api.config import settings


def get_http_status_message(code: int) -> str:
    return HTTPStatus(code).phrase


def get_audio_path_for_job(job_id: str) -> str:
    return os.path.join(settings.DOWNLOAD_PATH, job_id + "." + settings.PREFERREDCODEC)
