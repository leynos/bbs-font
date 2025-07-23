"""Utilities to render a single raised block from bitmap coordinates."""

from __future__ import annotations

import re
import typing

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc


def bitmap_to_ascii(bitmap: cabc.Iterable[str]) -> str:
    """Return a pseudo-3D representation of ``bitmap``.

    The bitmap must contain exactly one ``"1"``. Each row must be the same
    length. The output consists of ``height + 1`` lines. The top and bottom
    edges are a run of underscores. The raised block is drawn across the two
    rows that border its ``1``.
    """

    rows = list(bitmap)
    if not rows:
        raise ValueError("bitmap cannot be empty")

    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            raise ValueError("bitmap rows must have equal width")

    coords: list[tuple[int, int]] = []
    for r, row in enumerate(rows):
        for c, char in enumerate(row):
            if char == "1":
                coords.append((r, c))
                break

    if len(coords) != 1:
        raise ValueError(f"bitmap must contain exactly one '1', found {len(coords)}")
    y, x = coords[0]

    art_width = 2 * width + len(rows)
    top_line = "_" * (2 * width)
    top_shape = "/" + "\\" * 3
    bottom_shape = "\\" + "/" * 3

    line2_pre = "_" * (2 * x)
    line2 = (
        " " * y
        + line2_pre
        + top_shape
        + "_" * (art_width - len(" " * y) - len(line2_pre) - len(top_shape))
    )

    line3_pre = "_" * max(0, 2 * x - 1)
    line3 = (
        " " * (y + 1)
        + line3_pre
        + bottom_shape
        + "_" * (art_width - len(" " * (y + 1)) - len(line3_pre) - len(bottom_shape))
    )

    bottom_line = " " * len(rows) + "_" * (2 * width)
    return "\n".join([top_line, line2, line3, bottom_line])


def validate_ascii(art: str, width: int, height: int) -> None:
    """Validate ``art`` conforms to expected block layout."""

    lines = art.splitlines()
    if len(lines) != 4:
        raise AssertionError("wrong line count")

    if lines[0] != "_" * (2 * width):
        raise AssertionError("invalid top line")
    if not lines[-1].startswith(" " * height) or not lines[-1].endswith(
        "_" * (2 * width)
    ):
        raise AssertionError("invalid bottom line")

    slash_count = art.count("/")
    backslash_count = art.count("\\")
    if slash_count != 4 or backslash_count != 4:
        raise AssertionError("wrong number of slashes")

    def longest_run(ch: str) -> int:
        runs = [len(m.group(0)) for m in re.finditer(re.escape(ch) + "+", art)]
        return max(runs) if runs else 0

    if longest_run("_") < 2 * width:
        raise AssertionError("underscores too short")
    if longest_run("/") < 3 or longest_run("\\") < 3:
        raise AssertionError("slash groups too short")
