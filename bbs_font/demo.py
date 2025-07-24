"""Command-line demonstration of the ASCII renderer."""

from __future__ import annotations

from bbs_font.ascii_art import bitmap_to_ascii
from bbs_font.random_bitmap import random_bitmap

WIDTH = 6
HEIGHT = 4
COUNT = 5


def main() -> None:
    """Generate and print ``COUNT`` random bitmaps as ASCII art."""

    for i in range(COUNT):
        bitmap = random_bitmap(WIDTH, HEIGHT)
        art = bitmap_to_ascii(bitmap)
        print(art)
        if i < COUNT - 1:
            print()


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    main()
