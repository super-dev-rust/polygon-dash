import random

from tdigest import TDigest


def test_digest():
    t = TDigest(K=100)
    for i in range(1000):
        val = random.randint(1000, 5000)
        t.update(val)
    print(t.percentile(2))
    print(t.percentile(99))

    for i in range(100):
        t.update(random.randint(0, 100))

    print(t.percentile(5))
