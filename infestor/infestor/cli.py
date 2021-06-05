"""
Command line interface for the Humbug infestor.
"""
import argparse
import os
import sys

from . import config, manage

REPORT_TYPES = {"system", "error", "custom"}


def handle_init(args: argparse.Namespace) -> None:
    config.initialize(
        args.repository,
        args.python_root,
        args.name,
        args.relative_imports,
        args.reporter_token,
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
    config.load_config(config_file, print_warnings=True)


def handle_token(args: argparse.Namespace) -> None:
    config_file = config.default_config_file(args.repository)
    config_object = config.set_reporter_token(
        config_file,
        config.python_root_relative_to_repository_root(
            args.repository, args.python_root
        ),
        args.token,
    )
    print(config_object)


def handle_setup(args: argparse.Namespace) -> None:
    manage.add_reporter(args.repository, args.python_root, args.reporter_filepath)


def handle_add(args: argparse.Namespace) -> None:
    if args.report_type == "system":
        manage.add_system_report(args.repository, args.python_root, args.submodule)
    else:
        print(f"Unsupported report_type ({args.report_type})", file=sys.stderr)


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
        "-n",
        "--name",
        required=True,
        help="Name of project (to identify integration)",
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
        "-P",
        "--python-root",
        required=True,
        help="Root directory for Python code/module you want to register a token for (this is the relevant key in infestor.json)",
    )
    token_parser.add_argument(
        "token", help="Reporting token generated from https://bugout.dev/account/teams"
    )
    token_parser.set_defaults(func=handle_token)

    setup_parser = subcommands.add_parser(
        "setup",
        description="Defines a reporter that can be used throughout a Python package to access reporting functionality",
    )
    setup_parser.add_argument(
        "-P",
        "--python-root",
        required=True,
        help="Root directory for Python code/module you want to setup reporting for (this is the relevant key in infestor.json)",
    )
    setup_parser.add_argument(
        "-o",
        "--reporter-filepath",
        required=False,
        default=None,
        help="Path (relative to Python root) at which we should set up the reporter integration",
    )
    setup_parser.set_defaults(func=handle_setup)

    add_parser = subcommands.add_parser(
        "add",
        description="Adds reporting code to a given module",
    )
    add_parser.add_argument(
        "report_type",
        choices=REPORT_TYPES,
        help="Type of report you would like to add to your code base",
    )
    add_parser.add_argument(
        "-P",
        "--python-root",
        required=True,
        help="Root directory for Python code/module you want to setup reporting for (this is the relevant key in infestor.json)",
    )
    add_parser.add_argument(
        "-m",
        "--submodule",
        default=None,
        help="Path (relative to Python root) to submodule in which to fire off a system report",
    )
    add_parser.set_defaults(func=handle_add)

    remove_parser = subcommands.add_parser(
        "remove", description="Removes reporting code from a given module"
    )
    add_parser.add_argument(
        "report_type",
        choices=REPORT_TYPES,
        help="Type of report you would like to add to your code base",
    )
    add_parser.add_argument(
        "-P",
        "--python-root",
        required=True,
        help="Root directory for Python code/module you want to setup reporting for (this is the relevant key in infestor.json)",
    )
    add_parser.add_argument(
        "-m",
        "--submodule",
        default=None,
        help="Path (relative to Python root) to submodule in which to fire off a system report",
    )
    add_parser.set_defaults(func=handle_add)

    return parser


def main() -> None:
    parser = generate_argument_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
