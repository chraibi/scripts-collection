import argparse
import logging as log
import sys

import statsmodels.api as sm
from matplotlib import pyplot as plt
from statsmodels.stats.outliers_influence import summary_table
import numpy as np


def updt(total, progress):
    """
    Displays or updates a console progress bar.

    Original source: https://stackoverflow.com/a/15860757/1391441
    """
    barLength, status = 20, ""
    progress = float(progress) / float(total)
    if progress >= 1.0:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 0),
        status
    )
    sys.stdout.write(text)
    sys.stdout.flush()


log.basicConfig(level=log.INFO, format="%(levelname)s : %(message)s")

parser = argparse.ArgumentParser(
    description="""read two files (x and y values) and find the best angle
    to rotate the data, leading to best fit.
    """
)
parser.add_argument("file", nargs=2, help="freesm1.txt vm1.txt")
parser.add_argument(
    "--plot",
    type=bool,
    nargs="?",
    const=True,
    default=False,
    help="""Make a plot for every theta and save as png files. [optional]
    Handy to make a video but slows a bit the script.
    If not used, only the plot for the optimal fit will be produced
    """,
)

parser.add_argument(
    "--step",
    type=float,
    default=0.01,
    help="""Discretization constant (default=0.01)
    """,
)
args = parser.parse_args()

log.info(f"step | {args.step}")
log.info(f"plot | {args.plot}")
log.info(f"file1| {args.file[0]}")
log.info(f"file2| {args.file[1]}\n")
log.info("calculating optimal theta ...")
file1 = args.file[0]
file2 = args.file[1]

factors = np.arange(0, 1, args.step)
thetas = np.pi * factors
optimal_theta = 0
MSE = []
# x and y columns.
xorig = np.loadtxt(file1, unpack=True)
yorig = np.loadtxt(file2, unpack=True)
save_results = {}
for i, theta in enumerate(thetas):
    updt(len(thetas), i + 1)
    x = np.copy(xorig)
    y = np.copy(yorig)
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta), np.cos(theta)]])
    Rinv = np.linalg.inv(R)

    XY = np.array([x, y])
    # ====== rotate data ====
    XY = np.dot(R, XY)
    xr = XY[0]
    yr = XY[1]
    # =======================
    X = sm.add_constant(xr)  # adds a column of 1 to x
    res = sm.OLS(yr, X).fit()
    # dir(res)
    st, data, ss2 = summary_table(res, alpha=0.05)
    fittedvalues = data[:, 2]
    predict_mean_se = data[:, 3]
    predict_mean_ci_low, predict_mean_ci_upp = data[:, 4:6].T
    predict_ci_low, predict_ci_upp = data[:, 6:8].T
    # ============ tmp variables
    xfittedvalues = np.array([xr, fittedvalues])
    predict_ci_low = np.array([xr, predict_ci_low])
    predict_ci_upp = np.array([xr, predict_ci_upp])
    predict_mean_ci_low = np.array([xr, predict_mean_ci_low])
    predict_mean_ci_upp = np.array([xr, predict_mean_ci_upp])
    # ====== rotate back ====
    XY = np.dot(Rinv, np.array([x, y]))
    xfittedvaluesR = np.dot(Rinv, xfittedvalues)
    predict_ci_lowR = np.dot(Rinv, predict_ci_low)
    predict_ci_uppR = np.dot(Rinv, predict_ci_upp)
    predict_mean_ci_lowR = np.dot(Rinv, predict_mean_ci_low)
    predict_mean_ci_uppR = np.dot(Rinv, predict_mean_ci_upp)
    save_results[theta] = xfittedvaluesR
    MSE.append(res.mse_resid)

print("------------------")
imin = np.argmin(MSE)
optimal_theta = thetas[imin]
log.info(f"Optimal theta: {optimal_theta:.3f}")
# plot the optimal fit
if not args.plot:
    plt.plot(x, y, ".", alpha=0.1, label="data")
    plt.plot(
        save_results[optimal_theta][0],
        save_results[optimal_theta][1], "r-", label="OLS"
    )
    plt.legend(loc="best")
    plt.xlabel("freesm")
    plt.ylabel("vm")
    plt.xlim([-0.5, 1.0])
    plt.ylim([0, 2])
    plt.title(f"$\\theta = {optimal_theta:.2f}^\\circ$")
    plt.savefig(f"theta_{optimal_theta:.2f}.png", dpi=600)
else:
    log.info("Ploting png files ...")
    for i, theta in enumerate(thetas):
        updt(len(thetas), i + 1)
        plt.plot(x, y, ".", alpha=0.1, label="data")
        if theta == optimal_theta:
            plt.plot(
                save_results[theta][0],
                save_results[theta][1], "r-", label="OLS"
            )
        else:
            plt.plot(
                save_results[theta][0],
                save_results[theta][1], "b-", label="OLS"
            )
        plt.legend(loc="best")
        plt.xlabel("freesm")
        plt.ylabel("vm")
        plt.xlim([-0.5, 1.0])
        plt.ylim([0, 2])
        plt.title(
            f"$\\theta = {theta:.2f}^\\circ$ | (MSE = {res.mse_resid:.3f})")
        plt.savefig(f"{i:03d}.png", dpi=600)
        plt.clf()       
