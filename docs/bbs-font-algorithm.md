# Bitmap to pseudo-3D conversion

A bitmap encodes one or two raised blocks. The renderer converts the grid into
a pseudo-3D view formed by four text rows. The first and last rows are the
floor and ceiling. Blocks are drawn across the middle two rows. A row of
underscores represents the floor of the grid. Each bitmap column expands to two
character columns in the output to simulate perspective. For a block at
position `(x, y)` (row `y`, column `x`):

1. The output width is at least `2 * cols + rows`. If a block sits near the
   boundary, the width expands so the second and third lines show the full
   shapes. The top line is `2 * cols` underscores. The bottom line uses `rows`
   leading spaces and pads underscores to the computed width.

2. Each block sits across the two rows that border its `1` in the bitmap.
   Blocks in the same row may touch horizontally. Vertically stacked blocks
   share edges so the rising edge of the lower block starts with a backslash
   instead of a forward slash. If the stack reaches the bitmap's bottom, the
   falling edge of the lower block is drawn on the final output line. When
   blocks touch horizontally, edges merge into a single shape. The number of
   slashes grows by two for each additional touching block:

    - The rising edge uses `"/"` followed by `2 * n + 1` backslashes where
      `n` is the number of horizontally touching blocks in that group. A
      solitary block therefore has a run of three backslashes.
    - The falling edge uses a backslash followed by `2 * n + 1` forward
      slashes.

3. Underscores fill the remaining space so that every line has the same width.

The approach avoids lookup tables by calculating offsets and padding based
solely on the bitmap dimensions and block coordinates. Groups are rendered from
left to right so touching blocks share slashes correctly.
