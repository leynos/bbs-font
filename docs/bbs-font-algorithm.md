# Pseudo-3D ASCII rendering algorithm

This document describes how the bitmap data for a font is transformed into the
pseudo‑3D ASCII representation used by this project. The algorithm does not rely
on a lookup table and works for any grid size.

## Overview

A bitmap is provided as a grid of `0` and `1` characters. Each `1` represents a
raised cube. The algorithm extrudes these cubes in an isometric view and outputs
lines of ASCII characters. The width of each output line is `2 * width + height`
characters and the height is `height + 1` lines.

The output is constructed in two phases:

1. **Base grid** – Create a canvas of spaces sized as above and draw the base
   plane using underscores. The `i`th output line begins with `i` spaces
   followed by `2 * width` underscores.
2. **Cubes** – Iterate over the bitmap from bottom row to top. For every `1` bit
   at `(row, col)` draw the visible faces of a cube on the canvas. Neighbouring
   cubes occlude internal edges so only exposed faces are rendered.

## Drawing a cube

For a cube located at `(row, col)` (measured from the top left corner of the
bitmap):

* `top_y = height - row - 1`
* `left_x = 2 * col + top_y`

The cube occupies three output rows starting at `top_y`. The exact characters
are placed according to the visibility of the top, left and right faces:

```text
row:   left_x           left_x + 1
----------------------------------
 top_y         "_/"        "\\\\"
 top_y + 1     "_"         "///"
 top_y + 2     "_"         "__"
```

When adjacent cubes share a face, that face is omitted so that the surfaces
merge seamlessly.

## Pseudocode

```python
from typing import Iterable, List

Cell = Iterable[Iterable[int]]

def render(bitmap: Cell) -> List[str]:
    height = len(bitmap)
    width = len(bitmap[0]) if height else 0
    canvas = [list(" " * (2 * width + height)) for _ in range(height + 1)]

    # Draw base plane
    for row in range(height + 1):
        start = row
        for col in range(2 * width):
            canvas[row][start + col] = "_"

    # Draw cubes from back to front
    for r in reversed(range(height)):
        for c in range(width):
            if bitmap[r][c] == 1:
                draw_cube(canvas, r, c)

    return ["".join(line).rstrip() for line in canvas]
```

The `draw_cube` function places the characters described in the table above only
for faces not hidden by neighbouring cubes.

This approach handles bitmaps of any size and builds the ASCII art directly from
the grid structure without resorting to pre–generated patterns.
