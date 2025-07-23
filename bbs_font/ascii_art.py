"""Utilities to render a single raised block from bitmap coordinates."""

from __future__ import annotations

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
        count = row.count("1")
        if count > 1:
            raise ValueError(f"bitmap row {r} contains multiple '1's")
        if count == 1:
            coords.append((r, row.index("1")))

    if len(coords) != 1:
        raise ValueError(f"bitmap must contain exactly one '1', found {len(coords)}")
    y, x = coords[0]

    art_width = 2 * width + len(rows)
    top_line = "_" * (2 * width)
    top_shape = "/" + "\\" * 3
    bottom_shape = "\\" + "/" * 3

    post2 = art_width - y - 2 * x - len(top_shape)
    line2 = " " * y + "_" * (2 * x) + top_shape + "_" * post2

    pre3 = max(0, 2 * x - 1)
    post3 = art_width - (y + 1) - pre3 - len(bottom_shape)
    line3 = " " * (y + 1) + "_" * pre3 + bottom_shape + "_" * post3

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
        max_run = curr = 0
        for c in art:
            if c == ch:
                curr += 1
                if curr > max_run:
                    max_run = curr
            else:
                curr = 0
        return max_run

    if longest_run("_") < 2 * width:
        raise AssertionError("underscores too short")
    if longest_run("/") < 3 or longest_run("\\") < 3:
        raise AssertionError("slash groups too short")
