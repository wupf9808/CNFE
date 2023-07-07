import math
import os
import sys
from time import perf_counter_ns
import socket

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


from CNFE.mife.cipher import Cipher
from CNFE.mife.params import ParameterBuilder
from CNFE.utils import RNG


def base2(val):
    o = round(math.log2(val))
    r = val - (1 << o)
    if r > 0:
        r = f"+{r}"
    return f"2**{o}" + (str(r) if r else "")


def get_param(ell, d):
    m = 1 << 5
    n = 1 << 6
    t = 1 << 10

    p_1 = 2**23 + 9
    p_2 = 2**67 + 3
    lam = 2**156
    log_alpha = -322
    q = 2**326 + 249

    return ParameterBuilder(m, n, t)(ell, d, p_1, p_2, q, log_alpha)


def test(num_total, d):
    param = get_param(num_total, d)
    e = RNG.normal(param.lin.sd, ())

    ret = {
        'hostname': socket.gethostname()
        "ell": base2(param.ell),
        "d": base2(param.d),
        "lin.ell": base2(param.lin.ell),
        "lin.m": base2(param.lin.m),
        "lin.n": base2(param.lin.n),
        "lin.t": base2(param.lin.t),
        "lin.p_1": base2(param.lin.p_1),
        "lin.p_2": base2(param.lin.p_2),
        "lin.lam": base2(param.lin.lam),
        "lin.q": base2(param.lin.q),
        "lin.sd": base2(param.lin.sd),
    }

    x_vec = [RNG.uniform(param.lin.p_1, (param.ell // d,)) for _ in range(d)]
    y_vec = [RNG.uniform(param.lin.p_1, (param.ell // d,)) for _ in range(d)]

    cipher = Cipher(param)

    start = perf_counter_ns()

    # setup
    pps, msks = cipher.setup(d)
    ret["SETUP"] = perf_counter_ns() - start

    # enc
    ct_vec = [cipher.encrypt(pp, msk, x) for pp, msk, x in zip(pps, msks, x_vec)]
    ret["ENCRYPT"] = perf_counter_ns() - start

    # keygen
    sk = cipher.keygen(d, msks, y_vec, e)
    ret["KEYGEN"] = perf_counter_ns() - start

    # dec
    res = cipher.decrypt(ct_vec, sk)
    ret["DECRYPT"] = perf_counter_ns() - start

    ret["expected"] = sum(x @ y for x, y in zip(x_vec, y_vec))
    ret["returned"] = res
    return ret


if __name__ == "__main__":
    import json
    from sys import argv, stdout

    json.dump(test(2 ** int(argv[1]), int(argv[2])), stdout, indent=4)
