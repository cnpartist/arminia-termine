import struct
import tempfile
import unittest
from pathlib import Path

from build import png_size


class PngSizeTest(unittest.TestCase):
    def write(self, data: bytes) -> Path:
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(data)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return Path(tmp.name)

    def test_reads_width_and_height_from_ihdr(self):
        header = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", 1920, 1080)
        self.assertEqual(png_size(self.write(header + b"\x08\x06\x00\x00\x00")), (1920, 1080))

    def test_rejects_non_png(self):
        with self.assertRaises(ValueError):
            png_size(self.write(b"<html>not a png</html>" + b"\x00" * 20))


if __name__ == "__main__":
    unittest.main()
