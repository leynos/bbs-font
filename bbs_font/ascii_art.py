"""Utilities to render a single raised block from bitmap coordinates."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc

# Number of consecutive slashes forming each edge of the block.
SLASH_RUN = 3


def _make_shapes(count: int) -> tuple[str, str]:
    """Return the rising and falling edge shapes for ``count`` blocks."""

    run = 2 * count + 1
    top = "/" + "\\" * run
    bottom = "\\" + "/" * run
    return top, bottom


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
        for c, ch in enumerate(row):
            if ch == "1":
                coords.append((r, c))

    if not coords or len(coords) > 2:
        raise ValueError(f"bitmap must contain one or two '1's, found {len(coords)}")

    if len(coords) == 2:
        (y0, x0), (y1, x1) = coords
        if (
            abs(y0 - y1) <= 1
            and abs(x0 - x1) <= 1
            and not (y0 == y1 and abs(x0 - x1) == 1)
        ):
            raise ValueError("pixels may only touch horizontally")

    coords.sort()

    if len(coords) == 1:
        groups = [(coords[0][0], [coords[0][1]])]
    else:
        (y0, x0), (y1, x1) = coords
        if y0 == y1 and abs(x0 - x1) == 1:
            groups = [(y0, sorted([x0, x1]))]
        else:
            groups = [(y0, [x0]), (y1, [x1])]

    min_y = min(y for y, _ in coords)
    prefix2 = min_y
    prefix3 = min_y + 1

    base_width = 2 * width + height
    art_width = base_width
    for y, xs in groups:
        xs.sort()
        n = len(xs)
        top_shape, bottom_shape = _make_shapes(n)
        start_top = prefix2 + (y - min_y) + 2 * xs[0]
        start_bottom = prefix3 + (y - min_y) + max(0, 2 * xs[0] - 1)
        art_width = max(
            art_width,
            start_top + len(top_shape),
            start_bottom + len(bottom_shape),
        )

    line2_chars = ["_"] * art_width
    line3_chars = ["_"] * art_width
    for i in range(prefix2):
        line2_chars[i] = " "
    for i in range(prefix3):
        line3_chars[i] = " "

    for y, xs in groups:
        xs.sort()
        n = len(xs)
        top_shape, bottom_shape = _make_shapes(n)
        start_top = prefix2 + (y - min_y) + 2 * xs[0]
        start_bottom = prefix3 + (y - min_y) + max(0, 2 * xs[0] - 1)
        for idx, ch in enumerate(top_shape):
            line2_chars[start_top + idx] = ch
        for idx, ch in enumerate(bottom_shape):
            line3_chars[start_bottom + idx] = ch

    top_line = "_" * (2 * width)
    line2 = "".join(line2_chars)
    line3 = "".join(line3_chars)
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
        for c, ch in enumerate(row):
            if ch == "1":
                coords.append((r, c))

    if not coords or len(coords) > 2:
        raise AsciiArtValidationError(
            f"bitmap must contain one or two '1's, found {len(coords)}"
        )

    if len(coords) == 2:
        (y0, x0), (y1, x1) = coords
        if (
            abs(y0 - y1) <= 1
            and abs(x0 - x1) <= 1
            and not (y0 == y1 and abs(x0 - x1) == 1)
        ):
            raise AsciiArtValidationError("pixels may only touch horizontally")

    coords.sort()

    expected_art = bitmap_to_ascii(bitmap)
    expected_width = len(expected_art.splitlines()[1])

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
    expected_slash_count = expected_art.count("/")
    expected_backslash_count = expected_art.count("\\")
    if (
        slash_count != expected_slash_count
        or backslash_count != expected_backslash_count
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
