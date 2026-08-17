"""Transformacions de la temperatura base del CSV."""

import random

def temperatura_variada(temperatura_base):
    """Aplica el factor 0.8–1.2 demanat a una temperatura del CSV."""
    return round(float(temperatura_base) * random.uniform(0.8, 1.2), 1)
