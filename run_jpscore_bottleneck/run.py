#!/usr/bin/env python

from itertools import product
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil
import subprocess
import glob
import numpy as np
import matplotlib.pyplot as plt
import random

#------------ change variables in this block before running -------
n_runs = 10
seeds = random.sample(range(1, 10000), n_runs)
numbers = range(5, 50, n_runs)
master_file = "master.xml"
jpscore = "./bin/jpscore"
#-----------------------------------------------------------------
# create directory 'files', where inifiles are saved.
# delete directory if exists.
path_files = Path("./files")
if Path.exists(path_files):
    shutil.rmtree(path_files)

Path.mkdir(path_files)    
#----------------------------------
PATH = os.path.abspath('')
TEMPLATE_ENVIRONMENT = Environment(
    autoescape=False,
    loader=FileSystemLoader(PATH),
    trim_blocks=False)

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def Product(variables):
    return list(product(*variables))

def create_inifile(fname, _seed, _number, _traj):
    context= {'seed':_seed, 
              "location":_traj,
              'number':_number, 
             }
    with open(fname, 'w') as f:
        xml = render_template(master_file, context)
        f.write(xml)

if __name__ == "__main__":        
    N_T = {}
    means = []
    std = []
    for (number, seed) in product(numbers, seeds):
        location = "traj_n{}_s{}".format(number, seed)
        inifile = "files/inifile_n{}_s{}.xml".format(number, seed)
        create_inifile(inifile, seed, number, location+".xml")
        subprocess.run([jpscore, inifile])
        flow_file = "results/flow_exit_id_0_{}.txt".format(location)
        data = np.loadtxt(flow_file)
        evac_time = data[-1,0]
        if number in N_T:
            N_T[number].append(evac_time)
        else:
            N_T[number] = [evac_time] 


    for n in N_T.keys():
        means.append(np.mean(N_T[n]))
        std.append(np.std(N_T[n]))

    plt.errorbar(numbers, means, std, linestyle='None', marker='o', color="blue")
    plt.grid(alpha=0.3)
    plt.xlabel("N")
    plt.ylabel("T / s")
    figname =  "N-T.pdf"
    print("--> ", figname)
    plt.savefig(figname)


