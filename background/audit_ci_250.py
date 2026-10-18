#!/usr/bin/env python3
"""What a 250-claim audit can certify about the < 2% unsupported-value target.

Prints, for k unsupported claims out of n = 250, the observed rate and the upper
95% confidence bound (exact Clopper-Pearson, two-sided and one-sided; Wilson).
Referenced from background/grant_claim_checks.md. Requires scipy.
"""
import math
from scipy.stats import beta

N = 250
Z = 1.959964


def wilson_upper(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c + r) / d


print(f"n = {N}")
print("k  observed  CP two-sided 95% upper  CP one-sided 95% upper  Wilson 95% upper")
for k in range(0, 8):
    cp2 = beta.ppf(0.975, k + 1, N - k)
    cp1 = beta.ppf(0.95, k + 1, N - k)
    print(f"{k:<2} {k / N:>7.1%}  {cp2:>22.2%}  {cp1:>22.2%}  {wilson_upper(k, N):>16.2%}")
