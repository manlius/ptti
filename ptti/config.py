__all__ = ["config_load"]

from ptti.plotting import plot_defaults
from collections import OrderedDict
import numpy as np
import yaml

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def numpy_funcs():
    funcs = ['beta', 'binomial', 'chisquare', 'choice', 'dirichlet', 'exponential', 'gamma',
             'geometric', 'gumbel', 'hypergeometric', 'laplace', 'logistic', 'lognormal',
             'logseries', 'multinomial', 'multivariate_normal', 'negative_binomial',
             'noncentral_chisquare', 'noncentral_f', 'normal', 'pareto', 'poisson', 'power',
             'rand', 'randint', 'randn', 'random_integers', 'random_sample', 'rayleigh',
             'standard_cauchy', 'standard_exponential', 'standard_gamma', 'standard_normal',
             'standard_t', 'triangular', 'uniform', 'vonmises', 'wald', 'weibull', 'zipf']
    return { f: getattr(np.random, f) for f in funcs }

def config_load(filename=None, sample=0):
    """
    Load a YAML configuration file, supporting evaluation of some expressions and
    sensible defaults. The defaults are:

    {'initial': {'IU': 10, 'N': 1000},
     'interventions': {},
     'meta': {'model': 'SEIRCTODEMem',
              'output': 'simdata',
              'samples': 1,
              'steps': 3600,
              't0': 0,
              'tmax': 360},
     'parameters': {}}
    """
    if filename is not None:
        with open(filename) as fp:
            cfg = ordered_load(fp.read(), yaml.FullLoader)
    else:
        cfg = {}

    gvars = { "sample": sample }
    gvars.update(numpy_funcs())

    for k, v in cfg.items():
        ## collect global variables from initialisation
        if k == "initial":
            for i, iv in v.items():
                gvars[i] = iv

        ## compute global parameters
        if k == "parameters":
            v.update(_eval_params(v, gvars))

        if k == "interventions":
            for intv in v:
                for ik, iv in intv.items():
                    if ik == "parameters":
                        iv.update(_eval_params(iv, gvars))

    ## set some defaults
    cfg.setdefault("meta", {})
    cfg["meta"].setdefault("model", "SEIRCTODEMem")
    cfg["meta"].setdefault("t0", 0)
    cfg["meta"].setdefault("tmax", 365)
    cfg["meta"].setdefault("steps", 365)
    cfg["meta"].setdefault("samples", 1)
    cfg["meta"].setdefault("output", "simdata")
    cfg["meta"].setdefault("rseries", False)
    cfg["meta"].setdefault("plots", plot_defaults)
    cfg["meta"].setdefault("title", "PTTI Simulation")

    cfg.setdefault("initial", {})
    cfg["initial"].setdefault("N", 1000)
    cfg["initial"].setdefault("IU", 10)

    cfg.setdefault("parameters", {})
    cfg.setdefault("interventions", {})

    return cfg

def _eval_params(d, gvars):
    """
    Warning, mutates the gvars dictionary by adding parameters into it
    """
    params = {}
    for k, v in d.items():
        if isinstance(v, str):
            params[k] = eval(v, gvars)
        else:
            params[k] = v
        gvars[k] = params[k]
        #print("setting {} to {} = {}".format(k, v, params[k]))
    return params