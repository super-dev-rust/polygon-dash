import math


def activity_coef(num_txs, max_txs) -> float:
    c = num_txs / max_txs
    d = 1 / (1 + math.exp(-6 * (c - 0.1)))
    return 1 if c == 1 else d


def trust_score(act_coef, num_injections, num_outliers, num_txs) -> float:
    return act_coef * (
        0.8 * (1 - (num_injections / num_txs) ** 0.4)
        + 0.2 * (1 - (num_outliers / num_txs) ** 0.4)
    )
