import math
import os
import sys
from datetime import datetime
from itertools import product
from time import perf_counter_ns

import pandas as pd
from rich import print
from rich.progress import MofNCompleteColumn, Progress, TimeElapsedColumn

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from CNFE.quad import Cipher, ParameterBuilder, PredefinedParameters, PublicParameter
from CNFE.utils.rng import RNG

SIGMA = 10


def base2(val):
    o = round(math.log2(val))
    r = val - (1 << o)
    if r > 0:
        r = f"+{r}"
    return f"2**{o}" + (str(r) if r else "")


def instance(param: PublicParameter) -> int:
    ret = param._asdict()
    del ret["lin"]

    ret["p_1"] = base2(param.p_1)
    ret["p_2"] = base2(param.p_2)
    ret["q"] = base2(param.q)
    ret["lin.p_1"] = base2(param.lin.p_1)
    ret["lin.p_2"] = base2(param.lin.p_2)
    ret["lin.lam"] = base2(param.lin.lam)
    ret["lin.q"] = base2(param.lin.q)

    try:
        assert param.lin.ell < 2**20
        assert param.lin.ell * param.lin.n < 2**27
    except AssertionError:
        return ret

    x = RNG.uniform(param.p_1, (param.ell,))
    a = RNG.uniform(param.p_1, (param.ell, param.ell))

    cipher = Cipher(param)

    start = perf_counter_ns()

    pk, msk = cipher.setup()
    ret["SETUP"] = perf_counter_ns() - start

    reg = cipher.datareg()
    ret["DATAREG"] = perf_counter_ns() - start

    ct = cipher.encrypt(pk, x, reg)
    ret["ENCRYPT"] = perf_counter_ns() - start

    sk = cipher.keygen(pk, msk, a, SIGMA, reg)
    ret["KEYGEN"] = perf_counter_ns() - start

    res = cipher.decrypt(a, ct, sk)
    ret["DECRYPT"] = perf_counter_ns() - start

    ret["expected"] = x @ a @ x
    ret["returned"] = res

    return ret


def get_nproc():
    mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")


if __name__ == "__main__":
    FNAME = datetime.now().strftime("%Y%m%d-%H%M%S")

    parameters = []
    for _, log_n in product(range(1), range(5, 11)):
        parameters.extend(
            PredefinedParameters(ParameterBuilder(m=1 << 5, n=1 << log_n, t=1 << 10))
        )

    results = []

    with Progress(
        *Progress.get_default_columns(), MofNCompleteColumn(), TimeElapsedColumn()
    ) as progress:
        task = progress.add_task("Testing ...", total=len(parameters))

        for param in parameters:
            try:
                results.append(instance(param))
            except KeyboardInterrupt:
                raise
            except Exception as err:
                print(param)
                print(err)

            progress.advance(task)
            pd.DataFrame(results).to_csv(f"{FNAME}.quad.csv")

    # with ProcessPoolExecutor(max_workers=min(os.cpu_count() - 1, 64)) as executor:
    #     try:
    #         futures = [executor.submit(instance, param) for param in cases]

    #         with Progress(
    #             *Progress.get_default_columns(),
    #             MofNCompleteColumn(),
    #             TimeElapsedColumn(),
    #         ) as progress:
    #             task = progress.add_task("Testing ...", total=len(futures))

    #             for future in as_completed(futures):
    #                 results.append(future.result())
    #                 progress.advance(task)
    #                 pd.DataFrame(results).to_csv(f"{FNAME}.lin.csv")

    #     except KeyboardInterrupt:
    #         for pid in executor._processes:
    #             os.kill(pid, SIGKILL)
    #         raise
