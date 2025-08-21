import re
from pathlib import Path

import httpx
import pytest

from yt_dlp_api.transcription import transcript_aai


class TestTranscriptAssemblyAi:
    @pytest.mark.vcr
    async def test_transcript_aai(
        self, SAMPLE_HUMPTY_DUMPTY: Path, assembly_ai_client: httpx.AsyncClient
    ):
        expected_result = "Alice didn't know what to say to this. It wasn't at all like conversation, she thought, as he never said anything to her. In fact, his last remark was evidently addressed to a tree. So she stood and softly repeated to herself, humpty Dumpty sat on a wall. Humpty Dumpty had a great fall. All the King's horses and all the King's men couldn't put Humpty Dumpty in his place again."
        result = await transcript_aai(assembly_ai_client, str(SAMPLE_HUMPTY_DUMPTY))
        result_text = result["text"]

        assert result is not None, "Transcription result should not be None"

        # Not sure if anything below makes sense; Want to be sure we got anything meaningful back close to expected_result
        def normalize_text(text: str):
            text = text.lower()
            text = re.sub(r"[^\w\s]", "", text)
            return text

        normalized_expected = normalize_text(expected_result)
        normalized_result = normalize_text(result_text)

        # Check for word overlap
        expected_words = set(normalized_expected.split())
        result_words = set(normalized_result.split())

        common_words = expected_words.intersection(result_words)
        # Assert that at least 70% of expected words are present in the result
        assert len(common_words) / len(expected_words) >= 0.7, (
            "Insufficient word overlap in transcription"
        )

        # Check for length (allowing for some variation)
        assert len(normalized_result) > 0.8 * len(normalized_expected), (
            "Transcription result is too short"
        )
        assert len(normalized_result) < 1.2 * len(normalized_expected), (
            "Transcription result is too long"
        )
