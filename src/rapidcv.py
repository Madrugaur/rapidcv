"""Contains the logic to drive RapidCV"""
import os
import argparse
from typing import Dict, Set

from handler import Handler
from args import get_args


class RapidCV:
    """Tool to rapidly customize cover letters"""

    def validate_file(self, template_path: str) -> None:
        """Raises an error is provided path does not exists or does not point to a file

        Args:
            template_path (str): path to template file

        Raises:
            FileNotFoundError: if template_path does not exist
            TypeError: if template_path is not a file
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(template_path)

        if not os.path.isfile(template_path):
            raise TypeError(f"{template_path} is not a file")

    def get_file_handler(self, template_path: str, output_path: str) -> Handler:
        """Returns the correct file handler for the provided path

        Args:
            template_path (str): path to template file
            output_path (str): optional path to output file

        Raises:
            ValueError: if the extension of template_path is not supported

        Returns:
            Handler: a Handler for template_path
        """
        _, file_extension = os.path.splitext(template_path)
        if not Handler.is_supported(file_extension):
            raise ValueError(
                f"Extension '{file_extension}' is not supported."
                + " Supported extensions: {Handler.get_supported_file_types()}"
            )
        return Handler.get_handler(template_path, output_path, file_extension)

    def run_substitutions(
        self, handler: Handler, substitutions: Dict[str, str]
    ) -> None:
        """Calls the Handler to make the substitutions

        Args:
            handler (Handler): a Handler for template_path
            substitutions (Dict[str, str]): substitution key-value pairs

        Raises:
            ValueError: len(substitution) is 0
        """
        if len(substitutions.keys()) == 0:
            raise ValueError(
                "No substitutions provided, please use "
                + "interactive mode if you don't want provide any."
            )

        handler.make_substitutions(substitutions)

    def interactive_mode(self, handler: Handler, substitutions: Dict[str, str]) -> None:
        """Prompts the user to provide values for missing substitution keys in the template

        Args:
            handler (Handler): a Handler for template_path
            substitutions (Dict[str, str]): substitution key-value pairs
        """
        print(f"\n{'== RapidCV Interactive Mode ==':^80}")
        substitutions_keys: Set[str] = handler.parse_substitution_keys()
        unprovided_keys: Set[str] = substitutions_keys - set(substitutions.keys())
        print(
            f"{f'There are {len(unprovided_keys)} keys with no value provided, provide a value for these keys.':^80}\n"
        )
        for key in unprovided_keys:
            value: str = input(f"{key}: ")
            substitutions[key] = value

        self.run_substitutions(handler, substitutions)

    def main(self, args: argparse.Namespace) -> None:
        """Runs the RapidCV application

        Args:
            args (argparse.Namespace): CLI arguments
        """
        handler = self.get_file_handler(args.template, args.output)
        if args.interactive:
            self.interactive_mode(handler, args.substitutions)
        else:
            self.run_substitutions(handler, args.substitutions)


if __name__ == "__main__":
    RapidCV().main(get_args())
