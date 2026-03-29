#!/usr/bin/env python3
"""HyperLogLog for cardinality estimation of large datasets."""
import sys, hashlib, math

class HyperLogLog:
    def __init__(self, precision=14):
        self.p = precision; self.m = 1 << precision
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m) if self.m >= 128 else {16:0.673,32:0.697,64:0.709}[self.m]
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest()[:16], 16)
    def _rho(self, w):
        if w == 0: return 64 - self.p
        return min(64 - self.p, (w & -w).bit_length())
    def add(self, item):
        h = self._hash(item)
        idx = h & (self.m - 1)
        w = h >> self.p
        self.registers[idx] = max(self.registers[idx], self._rho(w))
    def count(self):
        Z = sum(2**(-r) for r in self.registers)
        E = self.alpha * self.m * self.m / Z
        # Small range correction
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0: E = self.m * math.log(self.m / V)
        return int(E)
    def merge(self, other):
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])

def main():
    import random; random.seed(42)
    hll = HyperLogLog(12)
    n_unique = 100000
    for i in range(n_unique): hll.add(f"user_{i}")
    # Add duplicates
    for i in range(50000): hll.add(f"user_{random.randint(0, n_unique-1)}")
    estimated = hll.count()
    error = abs(estimated - n_unique) / n_unique * 100
    print(f"  Actual unique: {n_unique:,}")
    print(f"  Estimated: {estimated:,}")
    print(f"  Error: {error:.2f}%")
    print(f"  Memory: {len(hll.registers)} registers ({len(hll.registers)*1} bytes)")
    # Merge test
    hll2 = HyperLogLog(12)
    for i in range(50000, 150000): hll2.add(f"user_{i}")
    hll.merge(hll2)
    print(f"  After merge: ~{hll.count():,} unique (expected ~150,000)")

if __name__ == "__main__": main()
