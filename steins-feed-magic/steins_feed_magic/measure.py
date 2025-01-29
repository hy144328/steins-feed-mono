import math

def entropy_bernoulli(p: float) -> float:
    if p == 0 or p == 1:
        return 0

    res = p * math.log2(p) + (1 - p) * math.log2(1 - p)
    return -res
