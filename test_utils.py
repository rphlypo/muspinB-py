import utils as f
import numpy as np

def test_loglikelihood_normal(k=1):
    mu0, sigma0 = 3, 2
    wt = np.array([f.draw_next_waiting_time(mu0, sigma0) for _ in range(1000)])
    mu, sigma = f.loglikelihood_lognormal(wt)
    np.testing.assert_almost_equal(mu, mu0, decimal=k)   # check whether equal on the first digit
    np.testing.assert_almost_equal(sigma, sigma0, decimal=k)   # check whether equal on the first digit

if __name__ == "__main__":
    test_loglikelihood_normal()