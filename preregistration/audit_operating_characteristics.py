#!/usr/bin/env python3
"""How each candidate success rule for the 250-claim audit behaves.

The grant commits to "< 2% of extracted values unsupported by their cited span,
audited on 250 claims" but does not say whether < 2% applies to the observed
rate or to an upper confidence bound. This script prints, for each candidate
rule, the largest number of unsupported claims that still passes, and the
probability of passing if the true unsupported rate is p.

Referenced from preregistration/analysis_plan.md (section 7.1) and DECISIONS.md
(D-02). Requires scipy.
"""
from scipy.stats import beta, binom

N = 250
TARGET = 0.02
TRUE_RATES = [0.0025, 0.005, 0.01, 0.015, 0.02, 0.03, 0.04]


def cp_upper(k, n, conf):
    """Exact Clopper-Pearson upper bound at the given one-sided confidence."""
    return 1.0 if k >= n else beta.ppf(conf, k + 1, n - k)


RULES = {
    "A: one-sided 95% CP upper bound < 2%": lambda k: cp_upper(k, N, 0.95) < TARGET,
    "B: two-sided 95% CP upper bound < 2%": lambda k: cp_upper(k, N, 0.975) < TARGET,
    "C: observed rate < 2%": lambda k: k / N < TARGET,
}

print(f"n = {N} audited claims, target < {TARGET:.0%} unsupported\n")
for name, passes in RULES.items():
    k_max = max(k for k in range(N + 1) if passes(k)) if passes(0) else None
    print(name)
    print(f"  passes with at most {k_max} unsupported claim(s)")
    for p in TRUE_RATES:
        print(f"  P(pass | true rate {p:.2%}) = {binom.cdf(k_max, N, p):.2f}")
    print()
