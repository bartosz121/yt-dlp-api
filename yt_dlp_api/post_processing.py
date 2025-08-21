import os
import subprocess

import structlog

log: structlog.stdlib.BoundLogger = structlog.get_logger()


def remove_silence(
    audio_path: str, *, replace_file: bool = False, output_path: str | None = None
) -> str:
    log.info(f"Removing silence for {audio_path!s}")

    if output_path:
        effective_output_path = output_path
    else:
        path, ext = os.path.splitext(audio_path)
        effective_output_path = f"{path}_silence_removed{ext}"

    cmd = [
        "ffmpeg",
        "-i",
        audio_path,
        "-af",
        "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB:stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB",
        "-y",
        effective_output_path,
    ]
    subprocess.run(cmd, check=True)

    if replace_file and not output_path:
        os.replace(effective_output_path, audio_path)
        log.info(f"Silence removed and file replaced for {audio_path}")
        return audio_path
    else:
        log.info(f"Silence removed. New file at {effective_output_path}")
        return effective_output_path


def speed_up_audio(
    audio_path: str,
    speed: float = 2.0,
    *,
    replace_file: bool = False,
    output_path: str | None = None,
) -> str:
    log.info(f"Speeding up audio for {audio_path!s}")

    if output_path:
        effective_output_path = output_path
    else:
        path, ext = os.path.splitext(audio_path)
        effective_output_path = f"{path}_speed_up{ext}"

    cmd = [
        "ffmpeg",
        "-i",
        audio_path,
        "-filter:a",
        f"atempo={speed}",
        "-y",
        effective_output_path,
    ]

    subprocess.run(cmd, check=True)

    if replace_file and not output_path:
        os.replace(effective_output_path, audio_path)
        log.info(f"Audio speed up and file replaced for {audio_path}")
        return audio_path
    else:
        log.info(f"Audio speed up. New file at {effective_output_path}")
        return effective_output_path
