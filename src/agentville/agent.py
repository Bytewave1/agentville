"""Agents. For now they decide at random; the LLM brain plugs in here later."""

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


@dataclass
class Agent:
    name: str
    x: int
    y: int
    rng: random.Random = field(default_factory=random.Random, repr=False)

    ACTIONS = ("north", "south", "west", "east", "wait")

    def decide(self, observation: Observation) -> str:
        """Pick an action. This is the seam where memory and an LLM will go."""
        return self.rng.choice(self.ACTIONS)
