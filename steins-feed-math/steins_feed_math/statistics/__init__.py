import random

class Reservoir[T]:
    def __init__(
        self,
        rng: random.Random,
        k: int,
    ):
        self.rng = rng
        self.k = k

        self.n = 0
        self.sample: list[T] = []
        self.sample_weights: list[float] = []

    def add(self, value: T, weight: float):
        if weight < 0:
            raise ValueError("Weight has to be non-negative.")

        if weight == 0:
            return

        self.n += weight

        if len(self.sample) < self.k:
            self.sample.append(value)
            self.sample_weights.append(weight)
        elif self.rng.random() < sum(self.sample_weights) / self.n:
            i = self._choice()
            self.sample[i] = value
            self.sample_weights[i] = weight

    def _choice(self) -> int:
        idxs = self.rng.choices(range(len(self.sample)), weights=self.sample_weights)
        return idxs[0]
