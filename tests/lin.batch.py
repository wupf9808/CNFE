import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from itertools import product
from signal import SIGKILL
from time import perf_counter_ns

import numpy as np
import pandas as pd
from rich.progress import MofNCompleteColumn, Progress, TimeElapsedColumn

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from CNFE.lin.cipher import Cipher
from CNFE.lin.params import ParameterBuilder, PredefinedParameters
from CNFE.utils.rng import RNG

SIGMA = 10
REPEAT = 32


cases = []
for _, log_n in product(range(REPEAT), range(5, 11)):
    cases.extend(
        PredefinedParameters(ParameterBuilder(m=1 << 5, n=1 << log_n, t=1 << 10))
    )


def base2(val):
    o = round(math.log2(val))
    r = val - (1 << o)
    if r > 0:
        r = f"+{r}"
    return f"2**{o}" + (str(r) if r else "")


def instance(param) -> int:
    ret = param._asdict()
    ret["p_1"] = base2(param.p_1)
    ret["p_2"] = base2(param.p_2)
    ret["lam"] = base2(param.lam)
    ret["q"] = base2(param.q)

    try:
        assert param.ell < 2**20
        assert param.ell * param.n < 2**27
    except AssertionError:
        return ret

    x = RNG.uniform(param.p_1, (param.ell,))
    y = RNG.uniform(param.p_1, (param.ell,))

    cipher = Cipher(param)

    start = perf_counter_ns()

    pk, msk = cipher.setup()
    ret["SETUP"] = perf_counter_ns() - start

    reg = cipher.datareg()
    ret["DATAREG"] = perf_counter_ns() - start

    ct = cipher.encrypt(pk, x, reg)
    ret["ENCRYPT"] = perf_counter_ns() - start

    sk = cipher.keygen(msk, y, SIGMA, reg)
    ret["KEYGEN"] = perf_counter_ns() - start

    res = cipher.decrypt(ct, sk)
    ret["DECRYPT"] = perf_counter_ns() - start

    ret["expected"] = x @ y
    ret["returned"] = res

    return ret


if __name__ == "__main__":
    FNAME = datetime.now().strftime("%Y%m%d-%H%M%S")

    results = []

    with ProcessPoolExecutor(max_workers=min(os.cpu_count() - 1, 64)) as executor:
        try:
            futures = [executor.submit(instance, param) for param in cases]

            with Progress(
                *Progress.get_default_columns(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task("Testing ...", total=len(futures))

                for future in as_completed(futures):
                    results.append(future.result())
                    progress.advance(task)
                    pd.DataFrame(results).to_csv(f"{FNAME}.lin.csv")

        except KeyboardInterrupt:
            for pid in executor._processes:
                os.kill(pid, SIGKILL)
            raise
