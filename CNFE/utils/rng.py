import secrets

import numpy as np
from numpy.random import default_rng

rng = default_rng(secrets.randbits(256))
MASK = (1 << 63) - 1


class RNG:
    # @staticmethod
    # def uniform(high: int, shape: tuple) -> np.ndarray:
    #     bytelen = high.bit_length() >> 3
    #     return np.frompyfunc(
    #         lambda: int.from_bytes(os.urandom(bytelen), "little") % high, 0, 1
    #     )(np.empty(shape, dtype=object))

    @staticmethod
    def uniform(high: int, shape: tuple) -> np.ndarray:
        _h = high

        ret = rng.integers(0, MASK, shape).astype(object)
        while _h:
            _h >>= 63
            ret = (ret << 63) | rng.integers(0, MASK, shape).astype(object)

        return ret % high

    @staticmethod
    def normal(scale, shape) -> np.ndarray:
        return np.abs(np.rint(rng.normal(0, scale, shape))).astype(int)

    @staticmethod
    def sample_noise(sigma) -> int:
        global rng
        rng = default_rng(secrets.randbits(256))
        return np.rint(rng.normal(0, sigma)).astype(int)
