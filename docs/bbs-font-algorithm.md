# Bitmap to pseudo-3D conversion

The algorithm interprets the bitmap as a flat grid with a single raised block.
A row of underscores represents the floor of the grid. For a block at position
`(x, y)` (row `y`, column `x`):

1. The output width is at least `2 * cols + rows`. If the block sits near the
   boundary, the width expands to fit the full shapes on the second and third
   lines. The top line is `2 * cols` underscores. The bottom line uses `rows`
   leading spaces and pads underscores to the computed width.
2. The block sits across the two rows that border the `1` in the bitmap:
   - The "rising" edge uses `"/"` followed by ``SLASH_RUN`` backslashes.
   - The "falling" edge uses a backslash followed by ``SLASH_RUN`` forward
     slashes.
   ``SLASH_RUN`` is currently ``3`` and shared by both the renderer and the
   validator.
3. Underscores fill the remaining space so that every line has the same width.

The approach avoids lookup tables by calculating offsets and padding based
solely on the bitmap dimensions and the block coordinates.
