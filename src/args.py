"""Provides logic for getting CLI args"""
import argparse
from typing import Any, Dict
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence


class ParseSubstitutions(argparse.Action):
    """Parses substitution key-value pairs when called"""

    def __init__(self, *args, **kwargs) -> None:
        self.args: Dict[str, str] = dict()
        super(ParseSubstitutions, self).__init__(*args, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        del parser
        del option_string
        for key, value in [arg.split("=", 2) for arg in values]:
            self.args[key] = value
        setattr(namespace, "substitutions", self.args)


def get_args() -> argparse.Namespace:
    """Creates an argparse parser and returns the parsed args

    Returns:
        argparse.Namespace: the parsed args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("template")
    parser.add_argument(
        "-i",
        "--interactive",
        required=False,
        default=False,
        action="store_true",
        help="Run in interactive mode, scanning the template for keys and prompting values for each",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default=None,
        help="Path to output file, defaults to the same name as the template",
    )
    parser.add_argument(
        "-s",
        "--substitutions",
        nargs="*",
        action=ParseSubstitutions,
        default={},
        help="Key-Value pairs corresponding to substitution keys in the template",
    )
    return parser.parse_args()
