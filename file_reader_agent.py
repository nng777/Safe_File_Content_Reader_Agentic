from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import argparse
import sys


class FileReaderTool(Protocol):
    #Protocol describing the signature of the file reading tool

    def __call__(self, path: Path) -> str:
        #Read the contents of *path* and return them as a string


@dataclass
class SafeFileContentAgent:
    #Agent responsible for safely reading the contents of a file.

    file_reader: FileReaderTool

    def confirm_action(self, path: Path) -> bool:
        #Ask the user to confirm whether the file should be read.

        prompt = f"Do you want to read the contents of '{path}'? (yes/no): "
        response = input(prompt).strip().lower()
        return response in {"y", "yes"}

    def read_file(self, path: Path) -> str:
        #Read *path* after ensuring it exists and can be accessed.

        if not path.exists():
            raise FileNotFoundError(f"The file '{path}' does not exist.")

        if path.is_dir():
            raise IsADirectoryError(f"'{path}' is a directory, not a file.")

        return self.file_reader(path)

    def run(self, path: Path) -> None:
        #Run the agent with the provided *path*.

        if not self.confirm_action(path):
            print("Action cancelled by the user.")
            return

        try:
            contents = self.read_file(path)
        except FileNotFoundError as exc:
            print(exc)
            return
        except IsADirectoryError as exc:
            print(exc)
            return
        except PermissionError:
            print(f"Permission denied when attempting to read '{path}'.")
            return
        except OSError as exc:  # Covers other OS-related errors
            print(f"An unexpected OS error occurred: {exc}")
            return

        print("\nFile contents:\n--------------------")
        print(contents)


def default_file_reader(path: Path) -> str:


    with path.open("r", encoding="utf-8") as file:
        return file.read()


def parse_args(argv: list[str]) -> argparse.Namespace:
    #Parse command-line arguments and return a namespace.

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to the file whose contents should be displayed.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    #Entry point for running the agent from the command line.

    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)

    file_path = Path(args.path) if args.path else Path(input("Enter the path to the file: ").strip())

    agent = SafeFileContentAgent(file_reader=default_file_reader)
    agent.run(file_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())