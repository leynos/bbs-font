from __future__ import annotations

import typing

if typing.TYPE_CHECKING:  # pragma: no cover - used only for type hints
    import collections.abc as cabc


def parse_bitmap(
    bitmap: cabc.Iterable[str],
    exc: type[Exception] = ValueError,
) -> tuple[int, int, list[tuple[int, int]]]:
    """Parse ``bitmap`` and extract coordinates of active pixels.

    Parameters
    ----------
    bitmap : cabc.Iterable[str]
        Iterable of strings representing the bitmap rows.
    exc : type[Exception], optional
        Exception type raised on validation failure. Defaults to ``ValueError``.

    Returns
    -------
    tuple[int, int, list[tuple[int, int]]]
        ``width``, ``height`` and a list of ``(row, col)`` coordinates for pixels
        set to ``"1"``.

    Raises
    ------
    exc
        If the bitmap is empty, non-rectangular, contains invalid characters or
        does not include one or two ``"1"`` pixels.
    """

    rows = list(bitmap)
    if not rows:
        raise exc("bitmap cannot be empty")

    width = len(rows[0])
    if width == 0:
        raise exc("bitmap rows may not be empty")
    height = len(rows)
    for row in rows:
        if len(row) != width:
            raise exc("bitmap rows must have equal width")
        for ch in row:
            if ch not in {"0", "1"}:
                raise exc("bitmap rows may only contain '0' and '1'")

    coords = [
        (r, c) for r, row in enumerate(rows) for c, ch in enumerate(row) if ch == "1"
    ]

    if not coords or len(coords) > 2:
        raise exc(f"bitmap must contain one or two '1's, found {len(coords)}")

    return width, height, coords


def validate_pixel_adjacency(coords: list[tuple[int, int]]) -> None:
    """Ensure two pixels, if present, only touch horizontally."""

    if len(coords) != 2:
        return
    (y0, x0), (y1, x1) = coords
    vertically_adjacent = abs(y0 - y1) == 1 and x0 == x1
    diagonally_adjacent = abs(y0 - y1) == 1 and abs(x0 - x1) == 1
    if vertically_adjacent or diagonally_adjacent:
        msg = f"pixels may only touch horizontally: {(y0, x0)} and {(y1, x1)}"
        raise ValueError(msg)

    horizontally_adjacent = y0 == y1 and abs(x0 - x1) == 1
    not_touching = abs(y0 - y1) > 1 or abs(x0 - x1) > 1
    if not (horizontally_adjacent or not_touching):
        msg = f"pixels may only touch horizontally: {(y0, x0)} and {(y1, x1)}"
        raise ValueError(msg)


def parse_and_validate_bitmap(
    bitmap: cabc.Iterable[str],
    exc: type[Exception] = ValueError,
) -> tuple[int, int, list[tuple[int, int]]]:
    """Parse ``bitmap`` and ensure any pixels only touch horizontally.

    Parameters
    ----------
    bitmap : cabc.Iterable[str]
        Iterable of strings representing the bitmap rows.
    exc : type[Exception], optional
        Exception type to raise on validation errors. Defaults to ``ValueError``.

    Returns
    -------
    tuple[int, int, list[tuple[int, int]]]
        ``width``, ``height`` and coordinates of ``"1"`` pixels.

    Raises
    ------
    exc
        If the bitmap fails basic validation or pixels touch vertically or
        diagonally.
    """

    width, height, coords = parse_bitmap(bitmap, exc)
    try:
        validate_pixel_adjacency(coords)
    except ValueError as err:
        raise exc(str(err)) from err
    return width, height, coords


def build_groups(
    coords: list[tuple[int, int]],
) -> tuple[list[tuple[int, list[int]]], int]:
    """Return groups of touching pixels and the minimum row."""

    coords_sorted = sorted(coords)
    if len(coords_sorted) == 1:
        groups = [(coords_sorted[0][0], [coords_sorted[0][1]])]
    else:
        (y0, x0), (y1, x1) = coords_sorted
        if y0 == y1 and abs(x0 - x1) == 1:
            groups = [(y0, sorted([x0, x1]))]
        else:
            groups = [(y0, [x0]), (y1, [x1])]
    min_y = coords_sorted[0][0]
    return groups, min_y
