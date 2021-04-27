"""
Command line interface for the Humbug infestor.
"""
import argparse
import json
import os

from . import config


def handle_init(args: argparse.Namespace) -> None:
    config.initialize(args.repository, args.reporter_token)
    print("Infestor has been initialized for your repository.\n")

    print(
        "The Bugout team collects crash reports as well as some basic, anonymous information about "
        "your system when you run infestor.\nWe do this so that we can improve the infestor "
        "experience for everyone.\nOf course, we understand if you want to turn off this reporting."
        "\nYou can do so at any time by setting the environment variable:\n"
        "\tINFESTOR_REPORTING_ENABLED=false\n"
    )
    print("In bash or zsh:\n\t$ export INFESTOR_REPORTING_ENABLED=false")
    print("In fish:\n\t$ set -x INFESTOR_REPORTING_ENABLED false")
    print("On Windows (cmd or powershell):\n\t$ set INFESTOR_REPORTING_ENABLED=false\n")

    if args.reporter_token is None:
        print(
            "It looks like you have not configured Infestor with a Bugout repoter token."
        )
        print(
            "Generate a reporter token by adding an integration to your team at https://bugout.dev/account/teams."
        )
        print("Once you have generated a token, run:")
        print("\t$ infestor token <token>\n")


def handle_token(args: argparse.Namespace) -> None:
    config_file = config.default_config_file(args.repository, create=False)
    config_object = config.set_reporter_token(config_file, args.token)
    print("Current configuration:")
    print(json.dumps(config_object, indent=2))


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
