import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from yt_dlp_api.post_processing import remove_silence, speed_up_audio

SAMPLES_DIR = Path(__file__).parent / "samples"
SAMPLE_WITH_SILENCE = SAMPLES_DIR / "sample_with_silence.m4a"
SAMPLE_FOR_SPEEDUP = SAMPLES_DIR / "sample_for_speedup.m4a"


def _get_duration(file_path: Path) -> float:
    """Returns the duration of an audio file in seconds."""
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


def _get_total_silence_duration(file_path: Path) -> float:
    cmd = [
        "ffmpeg",
        "-i",
        str(file_path),
        "-af",
        "silencedetect=n=-50dB:d=0.5",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    stderr_output = result.stderr

    silence_durations = re.findall(r"silence_duration: (\d+\.?\d*)", stderr_output)
    total_silence = sum(float(d) for d in silence_durations)
    return total_silence


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="ffmpeg/ffprobe not installed",
)
def test_remove_silence_with_output_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        temp_audio_path = tmpdir_path / "test.m4a"

        shutil.copy(SAMPLE_WITH_SILENCE, temp_audio_path)
        original_duration = _get_duration(temp_audio_path)
        total_silence = _get_total_silence_duration(temp_audio_path)
        expected_duration = original_duration - total_silence

        output_path = tmpdir_path / "output.m4a"
        returned_path_str = remove_silence(
            str(temp_audio_path), output_path=str(output_path)
        )
        returned_path = Path(returned_path_str)

        assert returned_path == output_path
        assert output_path.exists()
        new_duration = _get_duration(output_path)
        assert abs(new_duration - expected_duration) < 0.5
        assert _get_duration(temp_audio_path) == original_duration


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="ffmpeg/ffprobe not installed",
)
def test_speed_up_audio_with_output_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        temp_audio_path = tmpdir_path / "test.m4a"

        shutil.copy(SAMPLE_FOR_SPEEDUP, temp_audio_path)
        original_duration = _get_duration(temp_audio_path)
        speed = 2.0

        output_path = tmpdir_path / "output.m4a"
        returned_path_str = speed_up_audio(
            str(temp_audio_path), speed=speed, output_path=str(output_path)
        )
        returned_path = Path(returned_path_str)

        assert returned_path == output_path
        assert output_path.exists()

        new_duration = _get_duration(output_path)
        expected_duration = original_duration / speed
        assert abs(new_duration - expected_duration) < 0.1
        assert _get_duration(temp_audio_path) == original_duration
