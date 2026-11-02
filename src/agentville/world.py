"""The world: a small grid, a tick loop and the agents living in it."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .agent import Agent, Observation

# Direction name -> (dx, dy). The y axis grows downwards, like on a screen.
MOVES: dict[str, tuple[int, int]] = {
    "north": (0, -1),
    "south": (0, 1),
    "west": (-1, 0),
    "east": (1, 0),
}

DEFAULT_NAMES = ["Mia", "Tom", "Lena", "Ben", "Zoe"]


@dataclass
class Event:
    """Something that happened in the world. Later: the raw material for the town newspaper."""

    tick: int
    agent: str
    text: str


@dataclass
class World:
    width: int = 16
    height: int = 12
    seed: int | None = None
    tick: int = 0
    agents: list[Agent] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)

    # -- setup -------------------------------------------------------------

    def spawn(self, name: str) -> Agent:
        """Place a new agent on a free tile."""
        free = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self.agent_at(x, y) is None
        ]
        if not free:
            raise RuntimeError("The world is full.")
        x, y = self.rng.choice(free)
        agent = Agent(name=name, x=x, y=y, rng=random.Random(self.rng.random()))
        self.agents.append(agent)
        self.log(agent, f"moved to town at ({x}, {y})")
        return agent

    @classmethod
    def with_dummies(cls, count: int = 5, seed: int | None = None, **kwargs) -> "World":
        world = cls(seed=seed, **kwargs)
        for i in range(count):
            name = DEFAULT_NAMES[i] if i < len(DEFAULT_NAMES) else f"Agent{i + 1}"
            world.spawn(name)
        return world

    # -- queries -----------------------------------------------------------

    def agent_at(self, x: int, y: int) -> Agent | None:
        for agent in self.agents:
            if agent.x == x and agent.y == y:
                return agent
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def observe(self, agent: Agent, radius: int = 3) -> Observation:
        """What the agent can see right now."""
        nearby = [
            other.name
            for other in self.agents
            if other is not agent
            and abs(other.x - agent.x) <= radius
            and abs(other.y - agent.y) <= radius
        ]
        return Observation(tick=self.tick, x=agent.x, y=agent.y, nearby=nearby)

    # -- simulation --------------------------------------------------------

    def step(self) -> None:
        """Advance the world by one tick: perceive, decide, act."""
        self.tick += 1
        order = self.agents[:]
        self.rng.shuffle(order)  # nobody gets a permanent first-mover advantage
        for agent in order:
            action = agent.decide(self.observe(agent))
            self.apply(agent, action)

    def apply(self, agent: Agent, action: str) -> None:
        """The server decides what is legal. Agents only ask."""
        if action in MOVES:
            dx, dy = MOVES[action]
            nx, ny = agent.x + dx, agent.y + dy
            if self.in_bounds(nx, ny) and self.agent_at(nx, ny) is None:
                agent.x, agent.y = nx, ny
                self.log(agent, f"walked {action} to ({nx}, {ny})")
            else:
                self.log(agent, f"tried to walk {action} but was blocked")
        elif action == "wait":
            self.log(agent, "stood around")
        else:
            self.log(agent, f"tried unknown action {action!r}")

    def run(self, ticks: int) -> None:
        for _ in range(ticks):
            self.step()

    def log(self, agent: Agent, text: str) -> None:
        self.events.append(Event(tick=self.tick, agent=agent.name, text=text))

    def snapshot(self, max_events: int = 30) -> dict:
        """The world as plain data, ready to be sent to a browser as JSON."""
        return {
            "tick": self.tick,
            "width": self.width,
            "height": self.height,
            "agents": [{"name": a.name, "x": a.x, "y": a.y} for a in self.agents],
            "events": [
                {"tick": e.tick, "agent": e.agent, "text": e.text}
                for e in self.events[-max_events:]
            ],
        }

    # -- display -----------------------------------------------------------

    def render(self) -> str:
        """Tiny ASCII view of the town. Each agent is shown by their first letter."""
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                agent = self.agent_at(x, y)
                row.append(agent.name[0].upper() if agent else ".")
            rows.append(" ".join(row))
        return "\n".join(rows)
