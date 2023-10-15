
from scipy.stats import norm
import sympy


def norm_cdf_inverse(mass):
    """
    Inverse of normal cumulative distribution function.
    
    :param mass: probability mass
    :return: t such that P[x <= t] = mass for the mean 0 standard deviation 1 normal distribution
    """
    if isinstance(mass, sympy.Expr):
        # return a new symbol, if working symbolically
        return sympy.Symbol(f"norm_cdf_inverse({mass})", positive=True)
    return norm.ppf(float(mass))


def find_n_for_given_mass_of_binomial_left_of_threshold(
        *, 
        mass, 
        threshold,
        p1 = 0.5,
        p2 = 0.5,
        ):
    """
    Find n so that no more than a mass fraction of 
    Binomial(count=n, prob=0.5)/n - Binomial(count=n, prob=0.5)/n 
    is at or above threshold.
    This is from an approximation of this as normal with mean 0 
    and variance ((p1 * (1 - p1)) + (p2 * (1 - p2)) / n. 

    :param mass: probability we say difference of means should be no more than threshold.
    :param threshold: our point of comparison for observed difference in means.
    :param p1: assumed p1 probability bound (used for variance bound, can use 0.5 for upper bound).
    :param p2: assumed p2 probability bound (used for variance bound, can use 0.5 for upper bound).
    :return: n 
    """
    return (
        (norm_cdf_inverse(mass) / threshold)**2
        * ((p1 * (1 - p1)) + (p2 * (1 - p2)))
    )


def find_threshold_adjustment(
        *,
        power,
        significance,
):
    """
    get the threshold adjustment, find "a" such that:
    find_n_for_given_mass_of_binomial_left_of_threshold(mass=1-significance, threshold=a * r, p1, p2) =
        find_n_for_given_mass_of_binomial_left_of_threshold(mass=power, threshold=r - a * r, p1, p2)
    where r is the proposed change in rates effect size.
    
    :param power: proposed true positive rate
    :param significance: proposed false positive rate
    :return: threshold_adjustment "a" s.t. threshold = a * r
    """
    return 1 / (1 + norm_cdf_inverse(power) / norm_cdf_inverse(1 - significance))
