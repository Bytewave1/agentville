"""Agents. For now they wander at random; the LLM brain plugs in here later."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Observation:
    """What an agent perceives in a single tick."""

    tick: int
    x: int
    y: int
    nearby: list[str] = field(default_factory=list)
    # Directions the agent could actually walk in right now (free, walkable tiles).
    open: tuple[str, ...] = ()


@dataclass
class Agent:
    name: str
    x: int
    y: int
    rng: random.Random = field(default_factory=random.Random, repr=False)
    heading: str | None = field(default=None, repr=False)

    def decide(self, observation: Observation) -> str:
        """Pick an action. This is the seam where memory and an LLM will go.

        Agents keep walking in the same direction for a while, pause now and
        then and turn when something is in the way, which looks far more
        natural than a random step every tick.
        """
        options = list(observation.open)
        if not options or self.rng.random() < 0.12:
            return "wait"
        if self.heading in options and self.rng.random() < 0.8:
            return self.heading
        self.heading = self.rng.choice(options)
        return self.heading
