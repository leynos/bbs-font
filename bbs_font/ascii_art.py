"""Render pseudo-3D ASCII blocks from a bitmap."""

from __future__ import annotations

import typing

from .parser import build_groups, parse_and_validate_bitmap

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc


SLASH_RUN = 3


def _make_shapes(count: int) -> tuple[str, str]:
    """Return the rising and falling edge shapes for ``count`` blocks.

    Examples
    --------
    ``count=1`` yields ``("/\\\\\\", "\\/////")``.
    ``count=2`` yields ``("/\\\\\\\\\\", "\\///////")``.
    """

    run = 2 * count + 1
    return "/" + "\\" * run, "\\" + "/" * run


def _assemble_lines(
    width: int,
    height: int,
    groups: list[tuple[int, list[int]]],
    min_y: int,
) -> tuple[str, str, int]:
    """Return line2, line3 and total width for the ASCII art."""

    placements: list[tuple[int, str, int, str]] = []
    top_row_offset = min_y
    bottom_row_offset = min_y + 1

    for y, xs in groups:
        xs = sorted(xs)
        top_shape, bottom_shape = _make_shapes(len(xs))
        start_top = top_row_offset + (y - min_y) + 2 * xs[0]
        start_bottom = bottom_row_offset + (y - min_y) + max(0, 2 * xs[0] - 1)
        placements.append((start_top, top_shape, start_bottom, bottom_shape))

    art_width = 2 * width + height
    for st, top, sb, bottom in placements:
        art_width = max(art_width, st + len(top), sb + len(bottom))

    line2 = ["_"] * art_width
    line3 = ["_"] * art_width
    for i in range(top_row_offset):
        line2[i] = " "
    for i in range(bottom_row_offset):
        line3[i] = " "
    for st, top, sb, bottom in placements:
        for i, ch in enumerate(top):
            line2[st + i] = ch
        for i, ch in enumerate(bottom):
            line3[sb + i] = ch

    return "".join(line2), "".join(line3), art_width


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


class AsciiArtValidationError(Exception):
    """Raised when ASCII art validation fails."""


def bitmap_to_ascii(bitmap: cabc.Iterable[str]) -> str:
    """Return a pseudo-3D representation of ``bitmap``."""

    width, height, coords = parse_and_validate_bitmap(bitmap)
    groups, min_y = build_groups(coords)
    line2, line3, art_width = _assemble_lines(width, height, groups, min_y)

    top_line = "_" * (2 * width)
    bottom_line = " " * height + "_" * (art_width - height)
    return "\n".join([top_line, line2, line3, bottom_line])


def validate_ascii(art: str, bitmap: cabc.Iterable[str]) -> None:
    """Validate ``art`` conforms to expected block layout."""

    width, height, coords = parse_and_validate_bitmap(bitmap, AsciiArtValidationError)
    groups, min_y = build_groups(coords)
    line2, line3, expected_width = _assemble_lines(width, height, groups, min_y)

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
