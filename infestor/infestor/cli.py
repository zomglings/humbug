"""
Command line interface for the Humbug infestor.
"""
import argparse
import json
import os
import sys

from . import config


def handle_init(args: argparse.Namespace) -> None:
    config.initialize(
        args.repository, args.python_root, args.relative_imports, args.reporter_token
    )
    print("Infestor has been initialized for your repository.\n")

    print(
        "The Bugout team would like to collect crash reports as well as some basic, anonymous "
        "information about your system when you run infestor.\nThis will help us improve the "
        "infestor experience for everyone.\nWe request that you opt into reporting by setting the "
        "environment variable:\n"
        "\tINFESTOR_REPORTING_ENABLED=yes\n"
    )
    print("In bash or zsh:\n\t$ export INFESTOR_REPORTING_ENABLED=yes")
    print("In fish:\n\t$ set -x INFESTOR_REPORTING_ENABLED yes")
    print("On Windows (cmd or powershell):\n\t$ set INFESTOR_REPORTING_ENABLED=yes\n")

    if args.reporter_token is None:
        print(
            "It looks like you have not configured Infestor with a Bugout reporter token."
        )
        print(
            "Generate a reporter token by adding an integration to your team at https://bugout.dev/account/teams."
        )
        print("Once you have generated a token, run:")
        print("\t$ infestor token <token>\n")


def handle_validate(args: argparse.Namespace) -> None:
    config_file = config.default_config_file(args.repository)
    infestor_config = config.load_config(config_file)
    is_valid, warnings, errors = config.validate_config(infestor_config)
    if warnings:
        print(f"Warnings for configuration file: {config_file}:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print(f"Errors for configuration file: {config_file}:")
        for error in errors:
            print(f"- {error}")
    if not is_valid:
        sys.exit(1)


def handle_token(args: argparse.Namespace) -> None:
    config_file = config.default_config_file(args.repository)
    config_object = config.set_reporter_token(config_file, args.token)
    print(config_object)


def generate_argument_parser() -> argparse.ArgumentParser:
    current_working_directory = os.getcwd()

    parser = argparse.ArgumentParser(description="Humbug Infestor")
    parser.add_argument(
        "-r",
        "--repository",
        default=current_working_directory,
        help=f"Path to git repository containing your code base (default: {current_working_directory})",
    )
    parser.set_defaults(func=lambda _: parser.print_help())
    subcommands = parser.add_subparsers()

    init_parser = subcommands.add_parser("init")
    init_parser.add_argument(
        "-P",
        "--python-root",
        required=True,
        help=(
            "Root directory for Python code/module in the repository. If you are integrating with "
            "a module, this will be the highest-level directory with an __init__.py file in it."
        ),
    )
    init_parser.add_argument(
        "--relative-imports",
        action="store_true",
        help="Set this flags if infestor should add relative imports.",
    )
    init_parser.add_argument(
        "-t",
        "--reporter-token",
        default=None,
        help="Bugout reporter token. Get one by setting up an integration at https://bugout.dev/account/teams",
    )
    init_parser.set_defaults(func=handle_init)

    validate_parser = subcommands.add_parser("validate")
    validate_parser.set_defaults(func=handle_validate)

    token_parser = subcommands.add_parser("token")
    token_parser.add_argument(
        "token", help="Reporting token generated from https://bugout.dev/account/teams"
    )
    token_parser.set_defaults(func=handle_token)

    return parser


def main() -> None:
    parser = generate_argument_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
