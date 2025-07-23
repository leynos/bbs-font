# Bitmap to pseudo-3D conversion

The algorithm interprets the bitmap as a flat grid with a single raised block.
A row of underscores represents the floor of the grid. For a block at position
`(x, y)` (row `y`, column `x`):

1. The output width is `2 * cols + rows`. The top and bottom lines are
   underscores of length `2 * cols` with `rows` spaces of indentation on the
   bottom line.
2. The block sits across the two rows that border the `1` in the bitmap:
   - The "rising" edge uses `"/"` followed by three backslashes.
   - The "falling" edge uses a backslash followed by three forward slashes.
3. Underscores fill the remaining space so that every line has the same width.

The approach avoids lookup tables by calculating offsets and padding based
solely on the bitmap dimensions and the block coordinates.
