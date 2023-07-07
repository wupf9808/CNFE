import operator
from enum import IntEnum
from functools import reduce
from io import RawIOBase
from typing import Union

import gmpy2
import numpy as np

from CNFE import lin, quad


class CNFEType(IntEnum):
    LIN = 0x00
    QUAD = 0x80

    PARAMETER = 0x20
    ell = 0x21
    m = 0x22
    n = 0x23
    t = 0x24
    p_1 = 0x25
    p_2 = 0x26
    lam = 0x27
    q = 0x28
    sd = 0x29

    PK = 0x30
    A = 0x31  # lin
    U = 0x32  # lin
    u = 0x34  # quad

    MSK = 0x40
    Z = 0x41  # lin

    REG = 0x50
    r = 0x51  # lin

    CT = 0x60
    c0 = 0x61  # lin
    c1 = 0x61  # lin
    c = 0x64  # quad

    SK = 0x70
    ky = 0x71  # lin
    yhat = 0x72  # lin


class SerializerBase:
    t: CNFEType

    def __init__(self, io: RawIOBase) -> None:
        self.io: RawIOBase = io

    def _put_enum(self, val: int):
        assert val < 0x100
        return self.io.write(int.to_bytes(val | self.t, 1, "little"))

    def _put_int(self, val: int):
        assert isinstance(val, int) or isinstance(val, gmpy2.mpz)
        if val == 0:
            self.io.write(int.to_bytes(0, 1, "big"))
        else:
            raw = gmpy2.to_binary(gmpy2.mpz(val))[2:]
            self.io.write(int.to_bytes(len(raw), 1, "big"))
            self.io.write(raw)

    def _put_ndarray(self, val: np.ndarray, shape: Union[tuple, int]):
        if isinstance(shape, tuple):
            shape = reduce(operator.mul, shape)
        assert isinstance(shape, int)

        view = np.ravel(val)
        assert len(view) == shape

        for v in view:
            self._put_int(v)


class LinSerializer(SerializerBase):
    t = CNFEType.LIN

    def __init__(self, io: RawIOBase, param: lin.ParameterBuilder) -> None:
        super().__init__(io)
        assert isinstance(param, lin.PublicParameter)
        self.param = param

    def dump_param(self):
        self._put_enum(CNFEType.PARAMETER)
        self._put_enum(CNFEType.ell)
        self._put_int(self.param.ell)
        self._put_enum(CNFEType.m)
        self._put_int(self.param.m)
        self._put_enum(CNFEType.n)
        self._put_int(self.param.n)
        self._put_enum(CNFEType.t)
        self._put_int(self.param.t)
        self._put_enum(CNFEType.p_1)
        self._put_int(self.param.p_1)
        self._put_enum(CNFEType.p_2)
        self._put_int(self.param.p_2)
        self._put_enum(CNFEType.lam)
        self._put_int(self.param.lam)
        self._put_enum(CNFEType.q)
        self._put_int(self.param.q)
        self._put_enum(CNFEType.sd)
        self._put_int(self.param.sd)

    def dump_pk(self, pk: lin.cipher.PK):
        self._put_enum(CNFEType.PK)
        self._put_enum(CNFEType.A)
        self._put_ndarray(pk.A, (self.param.m, self.param.n))
        self._put_enum(CNFEType.U)
        self._put_ndarray(pk.U, (self.param.ell + self.param.t + 1, self.param.m))

    def dump_msk(self, msk: lin.cipher.MSK):
        self._put_enum(CNFEType.MSK)
        self._put_enum(CNFEType.Z)
        self._put_ndarray(msk.Z, (self.param.m, self.param.m))

    def dump_reg(self, reg: lin.cipher.REG):
        self._put_enum(CNFEType.REG)
        self._put_enum(CNFEType.r)
        self._put_ndarray(reg.r, (self.param.m, self.param.m))

    def dump_ct(self, ct: lin.cipher.CT):
        self._put_enum(CNFEType.CT)
        self._put_enum(CNFEType.c0)
        self._put_ndarray(ct.c0, self.param.m)
        self._put_enum(CNFEType.c1)
        self._put_ndarray(ct.c1, self.param.ell + self.param.t + 1)

    def dump_sk(self, sk: lin.cipher.SK):
        self._put_enum(CNFEType.SK)
        self._put_enum(CNFEType.ky)
        self._put_ndarray(sk.ky, self.param.m)
        self._put_enum(CNFEType.yhat)
        self._put_ndarray(sk.yhat, self.param.ell + self.param.t + 1)


class QuadSerializer(SerializerBase):
    t = CNFEType.QUAD

    def __init__(self, io: RawIOBase, param: quad.PublicParameter) -> None:
        super().__init__(io)
        assert isinstance(param, quad.PublicParameter)
        self.param = param
        self.lin = LinSerializer(io, param.lin)

    def dump_param(self):
        self._put_enum(CNFEType.PARAMETER)

        self._put_enum(CNFEType.ell)
        self._put_int(self.param.ell)
        self._put_enum(CNFEType.m)
        self._put_int(self.param.m)
        self._put_enum(CNFEType.n)
        self._put_int(self.param.n)
        self._put_enum(CNFEType.t)
        self._put_int(self.param.t)
        self._put_enum(CNFEType.p_1)
        self._put_int(self.param.p_1)
        self._put_enum(CNFEType.p_2)
        self._put_int(self.param.p_2)
        self._put_enum(CNFEType.q)
        self._put_int(self.param.q)
        self._put_enum(CNFEType.sd)
        self._put_int(self.param.sd)

        self.lin.dump_param()

    def dump_pk(self, pk: quad.cipher.PK):
        self._put_enum(CNFEType.PK)
        self._put_enum(CNFEType.u)
        self._put_ndarray(pk.u)

        self.lin.dump_pk(pk.lin)

    def dump_msk(self, msk: quad.cipher.MSK):
        self._put_enum(CNFEType.MSK)
        self.lin.dump_msk(msk.lin)

    def dump_reg(self, reg: quad.cipher.REG):
        self._put_enum(CNFEType.REG)
        self.lin.dump_reg(reg.lin)

    def dump_ct(self, ct: quad.cipher.CT):
        self._put_enum(CNFEType.CT)
        self._put_enum(CNFEType.c)
        self._put_ndarray(ct.c)
        self.lin.dump_ct(ct.lin)

    def dump_sk(self, sk: quad.cipher.SK):
        self._put_enum(CNFEType.SK)
        self.lin.dump_sk(sk.lin)
