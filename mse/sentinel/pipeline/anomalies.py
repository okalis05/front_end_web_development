import math
from dataclasses import dataclass

@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    z: float
    mean: float
    std: float

def rolling_zscore(history: list[float], current: float, min_n: int = 10) -> AnomalyResult:
    n = len(history)
    if n < min_n:
        mean = sum(history) / max(1, n)
        return AnomalyResult(False, 0.0, float(mean), 0.0)

    mean = sum(history) / n
    var = sum((v - mean) ** 2 for v in history) / max(1, (n - 1))
    std = math.sqrt(var) if var > 0 else 0.0
    if std == 0.0:
        return AnomalyResult(False, 0.0, float(mean), float(std))

    z = (current - mean) / std
    return AnomalyResult(abs(z) >= 2.2, float(z), float(mean), float(std))
