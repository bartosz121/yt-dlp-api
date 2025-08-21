from pathlib import Path

import httpx
import pytest


# https://github.com/kevin1024/vcrpy/issues/844
@pytest.fixture(autouse=True, scope="session")
def fix_patch_vcr():
    import vcr.stubs.httpx_stubs  # type: ignore
    from vcr.request import Request as VcrRequest  # type: ignore

    def _make_vcr_request(httpx_request, **kwargs):  # type: ignore
        body_bytes = httpx_request.read()  # type: ignore
        try:
            body = body_bytes.decode("utf-8")  # type: ignore
        except UnicodeDecodeError:
            body = body_bytes  # type: ignore
        uri = str(httpx_request.url)  # type: ignore
        headers = dict(httpx_request.headers)  # type: ignore
        return VcrRequest(httpx_request.method, uri, body, headers)  # type: ignore

    vcr.stubs.httpx_stubs._make_vcr_request = _make_vcr_request  # type: ignore


@pytest.fixture
def vcr_config():
    return {"filter_headers": ["Authorization"]}


@pytest.fixture
def SAMPLES_DIR():
    return Path(__file__).parent / "samples"


@pytest.fixture
def SAMPLE_WITH_SILENCE(SAMPLES_DIR: Path):
    return SAMPLES_DIR / "sample_with_silence.m4a"


@pytest.fixture
def SAMPLE_FOR_SPEEDUP(SAMPLES_DIR: Path):
    return SAMPLES_DIR / "sample_for_speedup.m4a"


@pytest.fixture
def SAMPLE_HUMPTY_DUMPTY(SAMPLES_DIR: Path):
    return SAMPLES_DIR / "HumptyDumptySample4416.flac"


@pytest.fixture
def assembly_ai_client() -> httpx.AsyncClient:
    from yt_dlp_api.config import settings

    return httpx.AsyncClient(
        base_url=settings.ASSEMBLY_AI_BASE_URL,
        headers={"Authorization": settings.ASSEMBLY_AI_KEY},
        timeout=60 * 5,
    )
