"""Render pseudo-3D ASCII blocks from a bitmap."""

from __future__ import annotations

import dataclasses as dc
import typing

from .parser import build_groups, parse_and_validate_bitmap

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc


# Geometry constants
# number of character steps per bitmap column in the pseudo perspective
COLUMN_STEP = 2
# length of the slash or backslash run representing one block edge
SINGLE_SLASH_RUN = 3
# width of one block including its trailing underscore
SINGLE_BLOCK_WIDTH = SINGLE_SLASH_RUN + 1


@dc.dataclass(slots=True)
class _Placement:
    """Represent the position and shapes of a block group."""

    top_start: int
    top_shape: str
    bottom_start: int
    bottom_shape: str


def _make_shapes(count: int) -> tuple[str, str]:
    """Return the rising and falling edge shapes for ``count`` blocks.

    Examples
    --------
    ``count=1`` yields ``("/\\", "\\///")``.
    ``count=2`` yields ``("/\\\\", "\\//////")``.
    """

    run = 2 * count + 1
    return "/" + "\\" * run, "\\" + "/" * run


def _place_shape(dest: list[str], shape: str, offset: int) -> None:
    """Place ``shape`` characters into ``dest`` starting at ``offset``."""

    for i, ch in enumerate(shape):
        dest[offset + i] = ch


def _compute_placements(
    groups: list[tuple[int, list[int]]],
    min_y: int,
    top_row_offset: int,
    bottom_row_offset: int,
) -> list[_Placement]:
    """Return placement data for each group."""

    placements: list[_Placement] = []
    for y, xs in groups:
        xs_sorted = sorted(xs)
        top_shape, bottom_shape = _make_shapes(len(xs_sorted))
        start_top = top_row_offset + (y - min_y) + COLUMN_STEP * xs_sorted[0]
        start_bottom = (
            bottom_row_offset + (y - min_y) + max(0, COLUMN_STEP * xs_sorted[0] - 1)
        )
        placements.append(_Placement(start_top, top_shape, start_bottom, bottom_shape))
    return placements


def _calc_art_width(width: int, height: int, placements: list[_Placement]) -> int:
    """Return the output width required for the art."""

    art_width = 2 * width + height
    for pl in placements:
        art_width = max(
            art_width,
            pl.top_start + len(pl.top_shape),
            pl.bottom_start + len(pl.bottom_shape),
        )
    return art_width


def _vertical_stack_info(
    groups: list[tuple[int, list[int]]],
) -> tuple[int, int, int] | None:
    """Return ``(top_y, bottom_y, x)`` if blocks form a vertical stack."""

    if (
        len(groups) == 2
        and len(groups[0][1]) == 1
        and len(groups[1][1]) == 1
        and groups[0][1][0] == groups[1][1][0]
        and abs(groups[0][0] - groups[1][0]) == 1
    ):
        top_y = min(groups[0][0], groups[1][0])
        bottom_y = max(groups[0][0], groups[1][0])
        return top_y, bottom_y, groups[0][1][0]
    return None


def _apply_vertical_stack(
    line2: list[str],
    line3: list[str],
    bottom_line: list[str],
    height: int,
    offset: int,
    bottom_y: int,
) -> None:
    """Adjust lines for vertically stacked blocks."""

    _place_shape(line2, "/" + "\\" * SINGLE_SLASH_RUN, offset)
    if offset + SINGLE_BLOCK_WIDTH < len(line2):
        line2[offset + SINGLE_BLOCK_WIDTH] = "_"

    line3[offset] = "\\"
    line3[offset + 1] = " "
    for i in range(SINGLE_SLASH_RUN):
        line3[offset + 2 + i] = "\\"

    if bottom_y == height - 1:
        for i, ch in enumerate("\\" + "/" * SINGLE_SLASH_RUN):
            idx = offset + 1 + i
            if idx < len(bottom_line):
                bottom_line[idx] = ch


def _assemble_lines(
    width: int,
    height: int,
    groups: list[tuple[int, list[int]]],
    min_y: int,
) -> tuple[str, str, str, int]:
    """Return rendered lines and total width for the ASCII art."""

    top_offset = min_y
    bottom_offset = min_y + 1
    placements = _compute_placements(groups, min_y, top_offset, bottom_offset)
    art_width = _calc_art_width(width, height, placements)

    line2 = ["_"] * art_width
    line3 = ["_"] * art_width
    bottom_line = list(" " * height + "_" * (art_width - height))

    for i in range(top_offset):
        line2[i] = " "
    for i in range(bottom_offset):
        line3[i] = " "

    for pl in placements:
        _place_shape(line2, pl.top_shape, pl.top_start)
        _place_shape(line3, pl.bottom_shape, pl.bottom_start)

    stack_info = _vertical_stack_info(groups)
    if stack_info:
        top_y, bottom_y, x = stack_info
        offset = top_offset + (top_y - min_y) + COLUMN_STEP * x
        _apply_vertical_stack(line2, line3, bottom_line, height, offset, bottom_y)

    return "".join(line2), "".join(line3), "".join(bottom_line), art_width


def _longest_run(text: str, ch: str) -> int:
    """Return the longest consecutive ``ch`` run found in ``text``."""

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
    line2, line3, bottom_line, art_width = _assemble_lines(width, height, groups, min_y)

    top_line = "_" * (2 * width)
    return "\n".join([top_line, line2, line3, bottom_line])


def validate_ascii(art: str, bitmap: cabc.Iterable[str]) -> None:
    """Validate ``art`` conforms to expected block layout."""

    width, height, coords = parse_and_validate_bitmap(bitmap, AsciiArtValidationError)
    groups, min_y = build_groups(coords)
    line2, line3, bottom_line, expected_width = _assemble_lines(
        width, height, groups, min_y
    )

    expected_slash_count = line2.count("/") + line3.count("/") + bottom_line.count("/")
    expected_backslash_count = (
        line2.count("\\") + line3.count("\\") + bottom_line.count("\\")
    )

    lines = art.splitlines()
    if len(lines) != 4:
        raise AsciiArtValidationError("wrong line count")

    if lines[0] != "_" * (2 * width):
        raise AsciiArtValidationError("invalid top line")
    if lines[-1] != bottom_line:
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
