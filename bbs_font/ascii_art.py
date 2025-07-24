"""Utilities to render a single raised block from bitmap coordinates."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc

# Number of consecutive slashes forming each edge of the block.
SLASH_RUN = 3


def _make_shapes(count: int) -> tuple[str, str]:
    """Return the rising and falling edge shapes for ``count`` blocks.

    Args:
        count: Number of horizontally adjacent blocks.

    Returns:
        A tuple ``(top, bottom)`` where ``top`` is the rising edge and
        ``bottom`` is the falling edge. Each edge consists of ``2 * count + 1``
        slashes plus a leading slash of the opposite type.
    """

    run = 2 * count + 1
    top = "/" + "\\" * run
    bottom = "\\" + "/" * run
    return top, bottom


def _place_shape(line: list[str], start: int, shape: str) -> None:
    """Place ``shape`` into ``line`` starting at ``start``."""

    for idx, ch in enumerate(shape):
        line[start + idx] = ch


class AsciiArtValidationError(Exception):
    """Raised when ASCII art validation fails."""


def _parse_bitmap(
    bitmap: cabc.Iterable[str],
    exc: type[Exception] = ValueError,
) -> tuple[int, int, list[tuple[int, int]]]:
    """Return ``width``, ``height`` and active pixel coordinates."""

    rows = list(bitmap)
    if not rows:
        raise exc("bitmap cannot be empty")

    width = len(rows[0])
    height = len(rows)
    for row in rows:
        if len(row) != width:
            raise exc("bitmap rows must have equal width")

    coords: list[tuple[int, int]] = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "1":
                coords.append((r, c))

    if not coords or len(coords) > 2:
        raise exc(f"bitmap must contain one or two '1's, found {len(coords)}")

    return width, height, coords


def _assemble_lines(
    width: int,
    height: int,
    groups: list[tuple[int, list[int]]],
    min_y: int,
    top_row_offset: int,
    bottom_row_offset: int,
) -> tuple[str, str, int]:
    """Build output lines and return them with the final width."""

    base_width = 2 * width + height
    art_width = base_width
    for y, xs in groups:
        xs.sort()
        top_shape, bottom_shape = _make_shapes(len(xs))
        start_top = top_row_offset + (y - min_y) + 2 * xs[0]
        start_bottom = bottom_row_offset + (y - min_y) + max(0, 2 * xs[0] - 1)
        art_width = max(
            art_width,
            start_top + len(top_shape),
            start_bottom + len(bottom_shape),
        )

    line2_chars = ["_"] * art_width
    line3_chars = ["_"] * art_width
    for i in range(top_row_offset):
        line2_chars[i] = " "
    for i in range(bottom_row_offset):
        line3_chars[i] = " "

    for y, xs in groups:
        xs.sort()
        top_shape, bottom_shape = _make_shapes(len(xs))
        start_top = top_row_offset + (y - min_y) + 2 * xs[0]
        start_bottom = bottom_row_offset + (y - min_y) + max(0, 2 * xs[0] - 1)
        _place_shape(line2_chars, start_top, top_shape)
        _place_shape(line3_chars, start_bottom, bottom_shape)

    return "".join(line2_chars), "".join(line3_chars), art_width


def _longest_run(text: str, ch: str) -> int:
    run = curr = 0
    for c in text:
        if c == ch:
            curr += 1
            if curr > run:
                run = curr
        else:
            curr = 0
    return run


def _validate_pixel_adjacency(coords: list[tuple[int, int]]) -> None:
    """Ensure two pixels, if present, only touch horizontally."""

    if len(coords) != 2:
        return
    (y0, x0), (y1, x1) = coords
    vertically_adjacent = abs(y0 - y1) == 1 and x0 == x1
    diagonally_adjacent = abs(y0 - y1) == 1 and abs(x0 - x1) == 1
    if vertically_adjacent or diagonally_adjacent:
        raise ValueError("pixels may only touch horizontally")


def _build_groups(
    coords: list[tuple[int, int]],
) -> tuple[list[tuple[int, list[int]]], int]:
    """Return groups of horizontally touching pixels and the minimum row."""

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
    return groups, min_y


def bitmap_to_ascii(bitmap: cabc.Iterable[str]) -> str:
    """Return a pseudo-3D representation of ``bitmap``.

    The bitmap may contain one or two ``"1"`` pixels. Each row must be the same
    length. The output consists of ``height + 1`` lines. The top and bottom edges
    are a run of underscores. Blocks are drawn across the two rows that border
    each ``"1"``. When two pixels are present they may only touch horizontally.
    """

    width, height, coords = _parse_bitmap(bitmap)
    _validate_pixel_adjacency(coords)

    groups, min_y = _build_groups(coords)
    top_row_offset = min_y
    bottom_row_offset = min_y + 1

    line2, line3, art_width = _assemble_lines(
        width, height, groups, min_y, top_row_offset, bottom_row_offset
    )

    top_line = "_" * (2 * width)
    bottom_line = " " * height + "_" * (art_width - height)
    return "\n".join([top_line, line2, line3, bottom_line])


def validate_ascii(art: str, bitmap: cabc.Iterable[str]) -> None:
    """Validate ``art`` conforms to expected block layout."""

    width, height, coords = _parse_bitmap(bitmap, AsciiArtValidationError)

    try:
        _validate_pixel_adjacency(coords)
    except ValueError as exc:  # pragma: no cover - should not happen in tests
        raise AsciiArtValidationError(str(exc)) from exc

    groups, min_y = _build_groups(coords)
    top_row_offset = min_y
    bottom_row_offset = min_y + 1

    line2, line3, expected_width = _assemble_lines(
        width, height, groups, min_y, top_row_offset, bottom_row_offset
    )

    expected_slash_count = line2.count("/") + line3.count("/")
    expected_backslash_count = line2.count("\\") + line3.count("\\")

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
        slash_count != expected_slash_count
        or backslash_count != expected_backslash_count
    ):
        raise AsciiArtValidationError("wrong number of slashes")

    if _longest_run(art, "_") < 2 * width:
        raise AsciiArtValidationError("underscores too short")
