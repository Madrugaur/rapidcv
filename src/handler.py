"""Contains the Handler base class and subclasses, allows substitution to be file-agnostic"""
from __future__ import annotations

import re
import os
from collections.abc import Iterable
from typing import Dict, Callable, Set

from docx import Document


class Handler:
    """Base class for all file handlers, provides common functions"""

    SUPPORTED_FILE_TYPES: Dict[str, "Handler"] = dict()
    SUBSTITUTION_KEY_REGEX: re.Pattern[str] = re.compile(r"\{\{(\w+)\}\}")
    OUTPUT_DIR: str = os.path.join(os.getcwd(), "output")

    def __init__(self, path: str, output_path: str) -> None:
        self.path = os.path.join(os.getcwd(), path)
        self.output_path = output_path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path})"

    def make_substitutions(self, substitutions: Dict[str, str]) -> None:
        """Uses the provided substitutions dict to replace all instances of a key with a value

        Raises:
            NotImplementedError: subclass has not implemented this function
        """
        del substitutions
        raise NotImplementedError()

    def parse_substitution_keys(self) -> Set[str]:
        """Returns a set of all substitution keys in the file

        Raises:
            NotImplementedError: subclass has not implemented this function
        """
        raise NotImplementedError()

    def make_replace_func(
        self, substitutions: Dict[str, str]
    ) -> Callable[[re.Match], str]:
        """Makes the replacement function for regex substitution

        Args:
            substitutions (Dict[str, str]): a list of substitution key-pair values that the
                                            resulting function can use for lookup

        Returns:
            Callable[[re.Match], str]: replacement function
        """

        def __replace(match: re.Match) -> str:
            key = match.group(1)

            if key not in substitutions.keys():
                print(f"Warning: No sub for '{key}' provided")
                return "{{" + key + "}}"

            return substitutions[key]

        return __replace

    def make_destination_file(self) -> str:
        """Generates a non-colliding destination path

        Returns:
            str: a unique path
        """
        custom_output = self.output_path is not None
        file_dir = (
            os.path.dirname(self.output_path) if custom_output else Handler.OUTPUT_DIR
        )
        if len(file_dir) == 0:
            file_dir = os.getcwd()
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        file_name: str = os.path.basename(
            self.output_path if custom_output else self.path
        )
        output_path: str = (
            os.path.join(os.getcwd(), self.output_path)
            if custom_output
            else os.path.join(Handler.OUTPUT_DIR, file_name)
        )
        if os.path.exists(output_path):
            file_base, file_ext = os.path.splitext(file_name)
            duplicate_number: int = len(
                [path for path in os.listdir(file_dir) if path.startswith(file_base)]
            )
            output_path = os.path.join(
                os.getcwd(), file_dir, f"{file_base}({duplicate_number}){file_ext}"
            )

        return output_path

    @staticmethod
    def get_handler(path: str, output_path: str, extension: str) -> "Handler":
        """Returns the Handler for the provided extension

        Args:
            path (str): path to template file
            output_path (str): path to output file
            extension (str): extension of template file

        Returns:
            Handler: a Handler for the provided extension
        """
        return Handler.SUPPORTED_FILE_TYPES[extension](path, output_path)

    @staticmethod
    def is_supported(extension: str) -> bool:
        """Checks if the provided extension is supported

        Args:
            extension (str): a template file extension

        Returns:
            bool: True if the extension is supported, False otherwise
        """
        return extension in Handler.SUPPORTED_FILE_TYPES

    @staticmethod
    def get_supported_file_types() -> str:
        """Returns a string containing a list of supported formats

        Returns:
            str: list of supported formats
        """
        return ", ".join(Handler.SUPPORTED_FILE_TYPES.keys())

    @classmethod
    def register_handler(
        self, extension: str or Iterable
    ) -> Callable[["Handler"], "Handler"]:
        """Registers a subclass as being able to parse a provided extension"""

        def register(subclass: "Handler") -> "Handler":
            if not isinstance(extension, str) and isinstance(extension, Iterable):
                for ext in extension:
                    Handler.SUPPORTED_FILE_TYPES[ext] = subclass
            else:
                Handler.SUPPORTED_FILE_TYPES[extension] = subclass

            return subclass

        return register


@Handler.register_handler(".txt")
class TextHandler(Handler):
    """Handler for Plain Text Files UTF-8 (txt)"""

    def make_substitutions(self, substitutions: Dict[str, str]) -> None:
        destination = self.make_destination_file()
        with open(self.path, "r", encoding="UTF-8") as template, open(
            self.make_destination_file(), "w+", encoding="UTF-8"
        ) as output:
            for line in template.readlines():
                subbed_line: str = re.sub(
                    Handler.SUBSTITUTION_KEY_REGEX,
                    self.make_replace_func(substitutions),
                    line,
                )
                output.write(subbed_line)
        print(destination)

    def parse_substitution_keys(self) -> Set[str]:
        substitution_keys: Set[str] = set()
        with open(self.path, "r", encoding="UTF-8") as template:
            for line in template.readlines():
                for key_match in re.finditer(Handler.SUBSTITUTION_KEY_REGEX, line):
                    substitution_keys.add(key_match.group(1))

        return substitution_keys


@Handler.register_handler(".docx")
class DocxHandler(Handler):
    """Handler for Microsoft Docx Files (docx)"""

    def make_substitutions(self, substitutions: Dict[str, str]) -> None:
        doc = Document(self.path)
        for paragraph in doc.paragraphs:
            subbed_paragraph: str = re.sub(
                Handler.SUBSTITUTION_KEY_REGEX,
                self.make_replace_func(substitutions),
                paragraph.text,
            )
            paragraph.text = subbed_paragraph
        doc.save(self.make_destination_file())

    def parse_substitution_keys(self) -> Set[str]:
        pass
