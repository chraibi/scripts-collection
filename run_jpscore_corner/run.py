#!/usr/bin/env python

import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader

jpscore = "/Users/chraibi/workspace/jupedsim/jpscore/build/bin/jpscore"
master_file = "master.xml"
tree = ET.parse('master.xml')
root = tree.getroot()
for tau in root.iter('tau'):
    T = tau.attrib

mu = T['mu']

# 1: GCFM
# 3: CVM
# https://www.jupedsim.org/jpscore_operativ.html
models = [1, 3]
# see wall_avoid_distance:
# below this wall-distance, the floor field will show a wall-repulsive
# character, directing agents away from the wall
# See https://www.jupedsim.org/jpscore_direction.html#strategy-8
wall_avoidance = [0.1, 0.5, 1.0]

# -----------------------------------------------------------------

# create directory 'tmp_jps_files', where inifiles are saved.
# delete directory if exists.
path_files = Path("./tmp_jps_files")
if Path.exists(path_files):
    shutil.rmtree(path_files)

Path.mkdir(path_files)
# ----------------------------------

PATH = os.path.abspath("")
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False, loader=FileSystemLoader(PATH), trim_blocks=False
)


def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def Product(variables):
    return list(product(*variables))


def create_inifile(fname, _model, _wall_avoidance, _traj):
    context = {
        "model": _model,
        "location": _traj,
        "wall": _wall_avoidance,
    }
    with open(fname, "w", encoding="utf8") as f:
        xml = render_template(master_file, context)
        f.write(xml)


def plot_geometry(axis):
    axis.plot([4, 0], [0, 0], "-k", lw=2)
    axis.plot([4, -3], [-3, -3], "-k", lw=2)
    axis.plot([4, -3], [-3, -3], "-k", lw=2)
    axis.plot([0, 0], [0, 4], "-k", lw=2)
    axis.plot([-3, -3], [-3, 4], "-k", lw=2)


# plot results
colors = {
    wall_avoidance[0]: "--r",
    wall_avoidance[1]: "-b",
    wall_avoidance[2]: "-.m",
}
subplots = {models[0]: 0, models[1]: 1}
titles = {models[0]: "GCFM", models[1]: "OVM"}


if __name__ == "__main__":
    # make simulations
    for (model, wall) in product(models, wall_avoidance):
        location = f"traj_m{model}_w{wall}"
        inifile = f"tmp_jps_files/inifile_m{model}_w{wall}.xml"
        create_inifile(inifile, model, wall, location + ".xml")
        subprocess.run([jpscore, inifile], check=True)

    # make plots
    fig, axs = plt.subplots(3, 2)
    for (model, wall) in product(models, wall_avoidance):
        trajectory_file = f"results/traj_m{model}_w{wall}.txt"
        data = np.loadtxt(trajectory_file)
        ids = np.unique(data[:, 0])
        for j, i in enumerate(ids):
            plot_geometry(axs[j, subplots[model]])
            d = data[data[:, 0] == i]
            axs[j, subplots[model]].plot(d[0, 2], d[0, 3], "ok")
            axs[j, subplots[model]].plot(
                d[:, 2], d[:, 3], colors[wall], label=f"$w_d$ = {wall}"
            )

        axs[0, subplots[model]].legend(bbox_to_anchor=(1.1, 1.2),
                                       loc='upper right',
                                       borderaxespad=0)
        axs[0, subplots[model]].set_title(titles[model])

fig.tight_layout()

print(f"corner-mu-{mu}.png")
plt.savefig(f"corner-{mu}.png", dpi=600)
