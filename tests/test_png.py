from __future__ import annotations

import struct
import unittest

from makeetheme.png import solid_png


class PngTests(unittest.TestCase):
    def test_solid_png_header_and_dimensions(self) -> None:
        data = solid_png(8, 9, (255, 0, 0, 255))
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (8, 9))


if __name__ == "__main__":
    unittest.main()
