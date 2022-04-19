import contextlib
import unittest
from collections import deque
from io import BytesIO

from edgedroid.data import load_default_trace

import common


class TestCommon(unittest.TestCase):
    def setUp(self) -> None:
        self.frames = load_default_trace("square00")

    def test_individual_packing_frames(self) -> None:
        for i in range(self.frames.step_count):
            frame_data = self.frames.get_frame(i, "success")
            eframe1 = common.EdgeDroidFrame(i + 1, frame_data)
            eframe2 = common.EdgeDroidFrame.unpack(eframe1.pack())

            self.assertEqual(eframe1, eframe2)

    def test_stream_packing_frames(self) -> None:
        frames = deque()
        stream_buf = BytesIO()

        for i in range(self.frames.step_count):
            frame_data = self.frames.get_frame(i, "success")
            frame = common.EdgeDroidFrame(i + 1, frame_data)
            frames.append(frame)
            stream_buf.write(frame.pack())

        stream_buf.seek(0)
        with contextlib.closing(common.frame_stream_unpack(stream_buf)) as unpacker:
            for orig_frame in frames:
                self.assertEqual(orig_frame, next(unpacker))

    def test_packing_responses(self) -> None:
        stream_buf = BytesIO()

        for resp in (True, False):
            packed = common.pack_response(resp)
            stream_buf.write(packed)

        stream_buf.seek(0)
        with contextlib.closing(common.response_stream_unpack(stream_buf)) as stream:
            for exp in (True, False):
                self.assertEqual(exp, next(stream))


if __name__ == "__main__":
    unittest.main()
