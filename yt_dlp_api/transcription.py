import asyncio
import time
from typing import Any

import httpx
import structlog

from yt_dlp_api.utils import get_audio_file_duration

log: structlog.stdlib.BoundLogger = structlog.get_logger()


async def _aai_upload_file(aai_client: httpx.AsyncClient, audio_file_path: str) -> str:
    with open(audio_file_path, "rb") as f:
        response = await aai_client.post("/v2/upload", content=f.read())
        audio_upload_data = response.json()
        log.debug(f"{audio_upload_data=}")

        return audio_upload_data["upload_url"]


async def _aai_transcript(
    aai_client: httpx.AsyncClient,
    upload_url: str,
    *,
    speech_model: str = "universal",
) -> str:
    transcript_payload = {
        "audio_url": upload_url,
        "speech_model": speech_model,
        "language_detection": True,
    }

    transcript_response = await aai_client.post("/v2/transcript", json=transcript_payload)
    transcript_data = transcript_response.json()

    log.debug(f"{transcript_data=}")
    transcript_id = transcript_data["id"]

    return transcript_id


async def _aai_poll_for_transcript_result(
    aai_client: httpx.AsyncClient,
    transcript_id: str,
    *,
    poll_interval: float = 5.0,
    timeout: float = 60.0 * 3,
) -> dict[str, Any]:
    start_time = time.monotonic()

    while True:
        if time.monotonic() - start_time > timeout:
            raise TimeoutError("Polling for transcript result timed out")

        transcript_response = await aai_client.get(f"/v2/transcript/{transcript_id}")
        transcript_data = transcript_response.json()
        log.debug(f"{transcript_data=}")

        if transcript_data["status"] == "completed":
            return transcript_data
        elif transcript_data["status"] == "error":
            raise RuntimeError(f"Transcription failed: {transcript_data['error']}")
        else:
            log.debug(f"{transcript_data["status"]=} sleeping {poll_interval!r}")
            await asyncio.sleep(poll_interval)


async def transcript_aai(
    aai_client: httpx.AsyncClient,
    audio_file_path: str,
    transcription_result_poll_interval: float = 60.0 * 3,
) -> dict[str, Any]:
    upload_url = await _aai_upload_file(aai_client, audio_file_path)
    transcript_id = await _aai_transcript(aai_client, upload_url)

    duration = get_audio_file_duration(audio_file_path)

    if duration > transcription_result_poll_interval:
        transcription_result_poll_interval = duration
        log.info(
            f"Transcription result poll interval changed to {transcription_result_poll_interval!r}"
        )

    transcription = await _aai_poll_for_transcript_result(
        aai_client, transcript_id, timeout=transcription_result_poll_interval
    )

    return transcription
