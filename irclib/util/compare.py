"""
IRC string comparison utilities
"""

import re

__all__ = ("match_mask",)

GLOB_MAP = {"?": ".", "*": ".*"}


def match_mask(mask: str, pattern: str) -> bool:
    """
    Match hostmask patterns in the standard banmask syntax (eg '*!*@host')
    """
    re_pattern = ""
    for c in pattern:
        re_pattern += GLOB_MAP.get(c, re.escape(c))

    regex = re.compile(f"^{re_pattern}$")
    return bool(regex.match(mask))
