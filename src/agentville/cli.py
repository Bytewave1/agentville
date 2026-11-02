"""Command line entry point: run the town for a few ticks and print it."""

from __future__ import annotations

import argparse

from .world import World


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="agentville", description="Run a tiny town of agents.")
    parser.add_argument("--ticks", type=int, default=10, help="how many ticks to simulate")
    parser.add_argument("--agents", type=int, default=5, help="how many dummy agents to spawn")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible runs")
    parser.add_argument("--quiet", action="store_true", help="only print the final map")
    args = parser.parse_args(argv)

    world = World.with_dummies(count=args.agents, seed=args.seed)

    if not args.quiet:
        print(f"Tick 0\n{world.render()}\n")

    for _ in range(args.ticks):
        world.step()
        if not args.quiet:
            print(f"Tick {world.tick}\n{world.render()}\n")

    if args.quiet:
        print(world.render())

    print("Last events:")
    for event in world.events[-5:]:
        print(f"  [{event.tick}] {event.agent} {event.text}")


if __name__ == "__main__":
    main()
