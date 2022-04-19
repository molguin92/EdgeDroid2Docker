import unittest

from edgedroid.data import load_default_trace

import common


class TestCommon(unittest.TestCase):
    def setUp(self) -> None:
        self.frames = load_default_trace("square00")

    def test_packing(self) -> None:
        for i in range(self.frames.step_count):
            frame_data = self.frames.get_frame(i, "success")
            eframe1 = common.EdgeDroidFrame(i + 1, frame_data)
            eframe2 = common.EdgeDroidFrame.unpack(eframe1.pack())

            self.assertEqual(eframe1, eframe2)


if __name__ == "__main__":
    unittest.main()
