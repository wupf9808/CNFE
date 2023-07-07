#!/usr/bin/env python3

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter

TIMING_N = 5
DURATION_COLS = ["Setup", "DataReg", "Enc", "KeyGen", "Dec"]


def load_experiment(fname):
    df = pd.read_csv(fname, index_col=0).dropna()
    df["Setup"] = df["SETUP"]
    df["DataReg"] = df["DATAREG"] - df["SETUP"]
    df["Enc"] = df["ENCRYPT"] - df["DATAREG"]
    df["KeyGen"] = df["KEYGEN"] - df["ENCRYPT"]
    df["Dec"] = df["DECRYPT"] - df["KEYGEN"]
    df["diff"] = df.apply(lambda r: int(r.returned) - int(r.expected), axis="columns")
    # df["returned"].astype(int) - df["expected"].astype(int)
    df[DURATION_COLS] = df[DURATION_COLS] / 1000000

    return df[
        [
            "ell",
            "m",
            "n",
            "t",
            "p_1",
            "p_2",
            "q",
            "sd",
            "lin.p_1",
            "lin.p_2",
            "lin.q",
            "lin.lam",
            "Setup",
            "DataReg",
            "Enc",
            "KeyGen",
            "Dec",
            "expected",
            "returned",
            "diff",
        ]
    ]


def plot_hist(noises: pd.Series, bins: int):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), dpi=120)
    ax.hist(noises, bins)
    ax.set_xlabel("Noise $e$")
    ax.set_ylabel("Relative Frequency")
    ax.yaxis.set_major_formatter(PercentFormatter(noises.count()))
    return fig


def aggregate(df):
    grp = df.groupby(["ell", "n"])[DURATION_COLS]
    desc = grp.describe()
    mean = grp.mean().reset_index()
    mean["ell"] = np.rint(np.log2(mean["ell"])).astype(int)
    mean["n"] = np.rint(np.log2(mean["n"])).astype(int)
    return desc, mean


def plot_timing(data, n):
    scope = data[data["n"] == n]

    fig, ax = plt.subplots(1, 1, figsize=(8, 5), dpi=120)
    for col, m in zip(DURATION_COLS, "D*o^s"):
        ax.plot(scope["ell"], scope[col], label=col, marker=m)

    ax.set_xlabel("Size of DataSet $\ell$ (log of 2)")
    ax.set_ylabel("Running Time (ms)")
    ax.set_yscale("log")
    ax.legend()
    return fig


def over_security_parameter(data, col):
    fig, ax = plt.subplots(1, 1, figsize=(8, 5), dpi=120)

    pivot = data.pivot(index="n", columns="ell", values=col)
    for col in pivot:
        ax.plot(pivot[col], label="$\\ell = 2^{{col}}$".replace("{col}", str(col)))
    ax.set_xlabel("Security Parameter $n$ (log of 2)")
    ax.set_ylabel("Running Time (ms)")
    ax.set_yscale("log")
    ax.legend()

    return pivot, fig


if __name__ == "__main__":
    # Check input file
    fname = Path(sys.argv[1])
    assert fname.is_file()
    df = load_experiment(fname)

    # Create output dir
    WORKDIR = fname.parent / fname.stem
    if WORKDIR.is_dir():
        shutil.rmtree(WORKDIR)
    WORKDIR.mkdir()

    with pd.ExcelWriter(WORKDIR / fname.with_suffix(".xlsx")) as WRITER:
        df.to_excel(WRITER, sheet_name="raw")

        fig = plot_hist(df["diff"], bins=12)
        fig.savefig(WORKDIR / "noise_hist.pdf")

        desc, mean = aggregate(df)
        desc.to_excel(WRITER, sheet_name="aggregated")

        fig = plot_timing(mean, TIMING_N)
        fig.savefig(WORKDIR / "comp_timing.pdf")

        pivot, fig = over_security_parameter(mean, "Setup")
        pivot.to_excel(WRITER, sheet_name="time_n_setup")
        fig.savefig(WORKDIR / "time_n_setup.pdf")

        pivot, fig = over_security_parameter(mean, "Enc")
        pivot.to_excel(WRITER, sheet_name="time_n_enc")
        fig.savefig(WORKDIR / "time_n_enc.pdf")

    # Create Archive
    shutil.make_archive(fname.stem, "zip", WORKDIR)
