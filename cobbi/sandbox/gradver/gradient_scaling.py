import torch
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil

from cobbi.core import gis, test_cases
from cobbi.core.utils import NonRGIGlacierDirectory
from cobbi.core.first_guess import compile_first_guess
from cobbi.core.inversion import InversionDirectory
from cobbi.core.dynamics import create_glacier
from cobbi.sandbox.gradver.cost_function import create_cost_func
from cobbi.core.inversion import InversionDirectory
from cobbi.core import data_logging
from cobbi.core.visualization import plot_gradient
from oggm import cfg
from scipy.optimize import approx_fprime

np.seed = 0  # needs to be fixed for reproducible results with noise

cfg.initialize()

basedir = '/path/to/example'
basedir = '/data/philipp/thesis_test2/Giluwe/gradient_verification_scaling/'

# TODO: think about IceThicknesses for case Giluwe
# Choose a case
case = test_cases.Giluwe
gdir = NonRGIGlacierDirectory(case, basedir)
# only needed once:
gis.define_nonrgi_glacier_region(gdir)

# create settings for inversion
lambdas = np.zeros(4)
lambdas[0] = 0.1  # TODO: better
lambdas[1] = 0.8  # TODO: really useful? (Better if smaller than 1 to focus
# on inner domain)
lambdas[2] = 2
lambdas[3] = 1e5


minimize_options = {
    'maxiter': 300,
    'ftol': 0.5e-3,
    #'xtol': 1e-30,
    'gtol': 1e-4,
    #'maxcor': 5,
    #'maxls': 10,
    'disp': True
}

gdir.write_inversion_settings(mb_spinup=None,
                              yrs_spinup=2000,
                              yrs_forward_run=200,
                              reg_parameters=lambdas,
                              solver='L-BFGS-B',
                              minimize_options=minimize_options,
                              inversion_subdir='3',
                              fg_shape_factor=1.,
                              bounds_min_max=(2, 600)
                              )

tbps = [None,]
# create_glacier(gdir)
first_guess = compile_first_guess(gdir) # TODO capsulate compile_first_guess in sole get_first guess
costs = []
grads = []
for tbp in tbps:
    cost_func = create_cost_func(gdir, use_AD=True, torch_backward_param=tbp)
    cost, grad = cost_func(first_guess)
    costs.append(cost)
    grads.append(grad)
    if tbp is None:
        name = 'tbp_None'
    else:
        name = 'tbp_{:g}'.format(tbp)
    filepath = os.path.join(gdir.dir, name + '.npy')
    np.save(filepath, grad)
    filepath = os.path.join(gdir.dir, name + '.png')
    plot_gradient(filepath, grad, name, ref_shape=first_guess.shape)

for db in [1, 0.1, 0.01, 0.001]:
    with torch.no_grad():
        cost_func2 = create_cost_func(gdir, use_AD=False)
        b = np.array(first_guess, dtype=np.float32).flatten()
        fin_dif_grad = approx_fprime(b, cost_func2, db)
    fin_dif_grad = fin_dif_grad.reshape(first_guess.shape)

    filepath = os.path.join(gdir.dir, 'fd_db_{:g}.npy'.format(db))
    np.save(filepath, fin_dif_grad)
    filepath = os.path.join(gdir.dir, 'fd_db_{:g}.png'.format(db))
    plot_gradient(filepath, fin_dif_grad,
                  'finite difference approximated gradient\n$db = {:g}m$'.format(db),
                  ref_shape=first_guess.shape)


    filepath = os.path.join(gdir.dir, 'abs_diff_db_{:g}.png'.format(db))
    plot_gradient(filepath, grad - fin_dif_grad,
                  'absolute difference of PyTorch AD and \n finite difference'
                  'gradient\n$db = {:g}m$'.format(db),
                  ref_shape=first_guess.shape)


print('end')