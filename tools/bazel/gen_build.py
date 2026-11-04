#!/usr/bin/env python3
"""Python entrypoints for the native generator build plan."""
import sys


def __getattr__(name):
    from _build_plan import get
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return get(name)
    except ValueError as error:
        raise AttributeError(name) from error


def main() -> int:
    from _build_plan import call
    try:
        return call("main")
    except ValueError as error:
        message = str(error).removeprefix("build-plan: ")
        if message.startswith("SystemExit: "):
            raise SystemExit(message.removeprefix("SystemExit: ")) from error
        raise


if __name__ == "__main__":
    if sys.argv[1:2] == ["--project-graph"]:
        import argparse
        from _support_data import request
        parser = argparse.ArgumentParser(description="Project the graph for one reader")
        parser.add_argument("generator")
        parser.add_argument("source")
        parser.add_argument("output")
        options = parser.parse_args(sys.argv[2:])
        request("project-graph-file", generator=options.generator,
                source=options.source, output=options.output)
    else:
        raise SystemExit(main())
