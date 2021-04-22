"""
Command line interface for the Humbug infestor.
"""
import argparse
import os

from . import config


def handle_init(args: argparse.Namespace) -> None:
    config.initialize(args.repository, args.reporter_token)
    print("Done!")


def handle_reporting(args: argparse.Namespace) -> None:
    config_file = config.default_config_file(args.repository, create=False)
    config.set_reporting_consent(config_file, args.consent == "on")
    print(f"Turned reporting {args.consent}")


def generate_argument_parser() -> argparse.ArgumentParser:
    current_working_directory = os.getcwd()

    parser = argparse.ArgumentParser(description="Humbug Infestor")
    parser.add_argument(
        "-r",
        "--repository",
        default=current_working_directory,
        help=f"Path to git repository containing your code base (default: {current_working_directory})",
    )
    subcommands = parser.add_subparsers()

    init_parser = subcommands.add_parser("init")
    init_parser.add_argument(
        "-t",
        "--reporter-token",
        default=None,
        help="Bugout reporter token. Get one by setting up an integration at https://bugout.dev/account/teams",
    )
    init_parser.set_defaults(func=handle_init)

    reporting_parser = subcommands.add_parser("reporting")
    reporting_parser.add_argument("consent", choices=["on", "off"])
    reporting_parser.set_defaults(func=handle_reporting)

    return parser


def main() -> None:
    parser = generate_argument_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
