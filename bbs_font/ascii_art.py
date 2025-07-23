"""Utilities to render a single raised block from bitmap coordinates."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc

# Number of consecutive slashes forming each edge of the block.
SLASH_RUN = 3

# Shapes used when rendering the block.
TOP_SHAPE = "/" + "\\" * SLASH_RUN
BOTTOM_SHAPE = "\\" + "/" * SLASH_RUN

# Expected slash counts derived from the shapes above.
EXPECTED_SLASH_COUNT = TOP_SHAPE.count("/") + BOTTOM_SHAPE.count("/")
EXPECTED_BACKSLASH_COUNT = TOP_SHAPE.count("\\") + BOTTOM_SHAPE.count("\\")


class AsciiArtValidationError(Exception):
    """Raised when ASCII art validation fails."""


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
    height = len(rows)
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

    base_width = 2 * width + height
    art_width = max(
        base_width,
        y + 2 * x + len(TOP_SHAPE),
        (y + 1) + max(0, 2 * x - 1) + len(BOTTOM_SHAPE),
    )
    top_line = "_" * (2 * width)
    top_shape = TOP_SHAPE
    bottom_shape = BOTTOM_SHAPE

    post2 = art_width - y - 2 * x - len(top_shape)
    line2 = f"{' ' * y}{'_' * (2 * x)}{top_shape}{'_' * max(0, post2)}"
    line2 = line2[:art_width].ljust(art_width, "_")

    pre3 = max(0, 2 * x - 1)
    post3 = art_width - (y + 1) - pre3 - len(bottom_shape)
    line3 = f"{' ' * (y + 1)}{'_' * pre3}{bottom_shape}{'_' * max(0, post3)}"
    line3 = line3[:art_width].ljust(art_width, "_")

    bottom_line = " " * height + "_" * (art_width - height)
    return "\n".join([top_line, line2, line3, bottom_line])


def validate_ascii(art: str, bitmap: cabc.Iterable[str]) -> None:
    """Validate ``art`` conforms to expected block layout."""

    rows = list(bitmap)
    if not rows:
        raise AsciiArtValidationError("bitmap cannot be empty")
    width = len(rows[0])
    height = len(rows)
    for row in rows:
        if len(row) != width:
            raise AsciiArtValidationError("bitmap rows must have equal width")

    coords: list[tuple[int, int]] = []
    for r, row in enumerate(rows):
        count = row.count("1")
        if count > 1:
            raise AsciiArtValidationError(f"bitmap row {r} contains multiple '1's")
        if count == 1:
            coords.append((r, row.index("1")))

    if len(coords) != 1:
        raise AsciiArtValidationError(
            f"bitmap must contain exactly one '1', found {len(coords)}"
        )
    y, x = coords[0]

    base_width = 2 * width + height
    expected_width = max(
        base_width,
        y + 2 * x + len(TOP_SHAPE),
        (y + 1) + max(0, 2 * x - 1) + len(BOTTOM_SHAPE),
    )

    lines = art.splitlines()
    if len(lines) != 4:
        raise AsciiArtValidationError("wrong line count")

    if lines[0] != "_" * (2 * width):
        raise AsciiArtValidationError("invalid top line")
    if not lines[-1].startswith(" " * height) or not lines[-1].endswith(
        "_" * (2 * width)
    ):
        raise AsciiArtValidationError("invalid bottom line")

    if (
        len(lines[1]) != expected_width
        or len(lines[2]) != expected_width
        or len(lines[3]) != expected_width
    ):
        raise AsciiArtValidationError("misaligned line width")

    slash_count = art.count("/")
    backslash_count = art.count("\\")
    if (
        slash_count != EXPECTED_SLASH_COUNT
        or backslash_count != EXPECTED_BACKSLASH_COUNT
    ):
        raise AsciiArtValidationError("wrong number of slashes")

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
        raise AsciiArtValidationError("underscores too short")
