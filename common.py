from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt

HEADER_PACK_FMT = "!IIIII"  # [seq][height][width][channels][data length]
HEADER_LEN = struct.calcsize(HEADER_PACK_FMT)
IMG_BYTES_ORDER = "C"


@dataclass
class EdgeDroidFrame:
    seq: int
    image_data: npt.NDArray

    def __eq__(self, other: Any):
        if not isinstance(other, EdgeDroidFrame):
            return False
        else:
            return self.seq == other.seq and (
                np.all(self.image_data == other.image_data)
            )

    def __post_init__(self):
        assert self.image_data.ndim == 3

    def pack(self) -> bytes:
        height, width, channels = self.image_data.shape
        img_data = self.image_data.tobytes(order=IMG_BYTES_ORDER)
        data_len = len(img_data)

        hdr = struct.pack(HEADER_PACK_FMT, self.seq, height, width, channels, data_len)

        return hdr + img_data

    @classmethod
    def unpack(cls, data: bytes) -> EdgeDroidFrame:
        hdr = data[:HEADER_LEN]
        seq, height, width, channels, data_len = struct.unpack(HEADER_PACK_FMT, hdr)
        image_data = np.frombuffer(
            data, offset=HEADER_LEN, count=data_len, dtype=np.uint8
        ).reshape((height, width, channels), order=IMG_BYTES_ORDER)

        return cls(seq, image_data)
