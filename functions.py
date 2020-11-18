from scipy.stats import lognorm
import numpy as np


def loglikelihood_lognormal(waiting_times):
    """ compute the most likely parameters for the log-normal law, given waiting times
    Arguments
    waiting_times   : array of waiting times in the process

    Returns
    mu      : mean of the lognormal variable
    sigma   : standard deviation of the lognormal variable
    """
    sigma, loc, scale = lognorm.fit(waiting_times, loc=0)
    mu = np.log(scale)
    return mu, sigma


def draw_next_waiting_time(mu, sigma):
    """ compute the waiting time until the next event, given lognormal distribution
    Arguments
    mu      : mean of the lognormal variable
    sigma   : standard deviation of the lognormal variable

    Returns
    t       : a single sample, specifying waiting time until the next event (flip)
    """

    X = lognorm(s=sigma, loc=0, scale=np.exp(mu))
    return X.rvs()
