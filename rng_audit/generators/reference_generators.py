"""Reference RNG Generators for Calibration Ladder.

Provides controlled data sources across the predictability spectrum:
1. Weak LCG (Linear Congruential Generator with low period / lattice defect)
2. Quadratic Non-Linear PRNG (Degree-2 algebraic recurrence)
3. Xorshift PRNG (Linear recurrence over GF(2))
4. Mersenne Twister PRNG (Standard deterministic PRNG)
5. Cryptographic RNG (CSPRNG / OS entropy null baseline)
"""

import os
import secrets
import time
from typing import List


class WeakLCG:
    """Weak Linear Congruential Generator: x_{n+1} = (a*x_n + c) mod m.
    Uses deliberately small modulus to create detectable hyperplane/lattice structure.
    """
    def __init__(self, seed: int = 12345, a: int = 65, c: int = 1, m: int = 2048):
        self.state = seed % m
        self.a = a
        self.c = c
        self.m = m

    def next_int(self, max_val: int = 100) -> int:
        self.state = (self.a * self.state + self.c) % self.m
        return self.state % max_val

    def generate_sequence(self, length: int, max_val: int = 100) -> List[int]:
        return [self.next_int(max_val) for _ in range(length)]


class QuadraticPRNG:
    """Non-linear Quadratic PRNG: x_{n+1} = (a*x_n^2 + b*x_n + c) mod m."""
    def __init__(self, seed: int = 42, a: int = 3, b: int = 5, c: int = 7, m: int = 8191):
        self.state = seed % m
        self.a = a
        self.b = b
        self.c = c
        self.m = m

    def next_int(self, max_val: int = 100) -> int:
        self.state = (self.a * self.state * self.state + self.b * self.state + self.c) % self.m
        return self.state % max_val

    def generate_sequence(self, length: int, max_val: int = 100) -> List[int]:
        return [self.next_int(max_val) for _ in range(length)]


class XorShift32:
    """XorShift 32-bit generator: Linear recurrence over GF(2)."""
    def __init__(self, seed: int = 2463534242):
        self.state = seed & 0xFFFFFFFF
        if self.state == 0:
            self.state = 1

    def next_int(self, max_val: int = 100) -> int:
        x = self.state
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= (x >> 17) & 0xFFFFFFFF
        x ^= (x << 5) & 0xFFFFFFFF
        self.state = x
        return (x % max_val)

    def generate_sequence(self, length: int, max_val: int = 100) -> List[int]:
        return [self.next_int(max_val) for _ in range(length)]


class MersenneTwisterPRNG:
    """Standard Python random (MT19937) with fixed seed."""
    def __init__(self, seed: int = 1337):
        import random
        self.rng = random.Random(seed)

    def next_int(self, max_val: int = 100) -> int:
        return self.rng.randint(0, max_val - 1)

    def generate_sequence(self, length: int, max_val: int = 100) -> List[int]:
        return [self.next_int(max_val) for _ in range(length)]


class CryptographicRNG:
    """Cryptographically Secure Pseudo-Random Generator (CSPRNG) using OS entropy.
    Serves as the rigorous null hypothesis baseline (no predictable algebraic structure).
    """
    def __init__(self):
        self.rng = secrets.SystemRandom()

    def next_int(self, max_val: int = 100) -> int:
        return self.rng.randrange(0, max_val)

    def generate_sequence(self, length: int, max_val: int = 100) -> List[int]:
        return [self.next_int(max_val) for _ in range(length)]
