import json
import os
import subprocess
from http import HTTPStatus
from pathlib import Path
from typing import Any

import httpx

from yt_dlp_api.config import settings


def get_assembly_ai_client(
    base_url: str | None = None,
    api_key: str | None = None,
    timeout: int = 60 * 5,
) -> httpx.AsyncClient:
    if base_url is None:
        base_url = settings.ASSEMBLY_AI_BASE_URL

    if api_key is None:
        api_key = settings.ASSEMBLY_AI_KEY

    return httpx.AsyncClient(
        base_url=base_url,
        headers={"Authorization": api_key},
        timeout=timeout,
    )


def get_http_status_message(code: int) -> str:
    return HTTPStatus(code).phrase


def get_audio_file_path_for_job(job_id: str) -> str:
    return os.path.join(settings.DOWNLOAD_PATH, job_id + "." + settings.PREFERREDCODEC)


def get_transcription_file_path_for_job(job_id: str) -> str:
    return os.path.join(settings.DOWNLOAD_PATH, job_id + ".json")


def get_audio_file_duration(file_path: Path | str) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout)


def read_transcription_data_from_file(download_job_id: str) -> dict[str, Any]:
    transcription_file_path = get_transcription_file_path_for_job(download_job_id)

    with open(transcription_file_path) as f:
        transcription_data = json.load(f)

        return transcription_data
