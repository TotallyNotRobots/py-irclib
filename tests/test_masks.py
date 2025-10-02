"""Test IRC string comparisons."""

from typing import TypedDict

import parser_tests.data
import pytest

from irclib.util.compare import match_mask


class MaskCase(TypedDict):
    """Mask match test case data."""

    mask: str
    matches: list[str]
    fails: list[str]


@pytest.mark.parametrize("data", parser_tests.data.mask_match["tests"])
def test_mask_match(data: MaskCase) -> None:
    """Test the mask matching logic."""
    pattern = data["mask"]

    for hostmask in data["matches"]:
        assert match_mask(hostmask, pattern)

    for hostmask in data["fails"]:
        assert not match_mask(hostmask, pattern)
