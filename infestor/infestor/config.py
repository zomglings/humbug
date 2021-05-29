"""
These are the tools infestor uses to set up a code base for automatic Humbug instrumentation.
"""
from dataclasses import asdict, dataclass
import json
import os
from typing import Dict, List, Optional, Tuple

from atomicwrites import atomic_write
from humbug.consent import HumbugConsent, environment_variable_opt_in, yes
from humbug.report import HumbugReporter

from .version import INFESTOR_VERSION

INFESTOR_REPORTING_TOKEN = "6ec64442-40e3-41ff-afe3-d818c023cd41"

infestor_consent = HumbugConsent(
    environment_variable_opt_in("INFESTOR_REPORTING_ENABLED", yes)
)

infestor_reporter = HumbugReporter(
    name=f"infestor",
    consent=infestor_consent,
    bugout_token=INFESTOR_REPORTING_TOKEN,
)

CONFIG_FILENAME = "infestor.json"


@dataclass
class InfestorConfiguration:
    python_root: str
    relative_imports: bool = False
    reporter_token: Optional[str] = None


REPORTER_TOKEN_KEY = "reporter_token"
PYTHON_ROOT_KEY = "python_root"
RELATIVE_IMPORTS_KEY = "relative_imports"


infestor_tags = [f"version:{INFESTOR_VERSION}"]


class ConfigurationError(Exception):
    """
    Raised if there is an issue with an infestor configuration file.
    """

    pass


def parse_config(
    raw_config: Dict[str, str]
) -> Tuple[InfestorConfiguration, List[str], List[str]]:
    """
    Checks if the given configuration is valid. If it is valid, returns (True, []) else returns
    (False, [<warnings>, ...], [<error messages>, ...]).
    """
    warn_messages: List[str] = []
    error_messages: List[str] = []

    python_root: Optional[str] = raw_config.get(PYTHON_ROOT_KEY)
    if python_root is None:
        error_messages.append("No Python root directory specified")
        python_root = ""

    relative_imports: Optional[bool] = raw_config.get(RELATIVE_IMPORTS_KEY)
    if relative_imports is None:
        error_messages.append(
            "Configuration does not specify whether or not to use relative imports"
        )
        relative_imports = False

    reporter_token: Optional[str] = raw_config.get(REPORTER_TOKEN_KEY)
    if reporter_token is None:
        warn_messages.append("No reporter token found")

    infestor_configuration = InfestorConfiguration(
        python_root=python_root,
        relative_imports=relative_imports,
        reporter_token=reporter_token,
    )

    return (infestor_configuration, warn_messages, error_messages)


def load_config(
    config_file: str, print_warnings: bool = False
) -> InfestorConfiguration:
    """
    Loads an infestor configuration from file and validates it.
    """
    try:
        with open(config_file, "r") as ifp:
            raw_config = json.load(ifp)
    except:
        raise ConfigurationError(f"Could not read configuration: {config_file}")

    configuration, warnings, errors = parse_config(raw_config)

    if print_warnings:
        warning_items = "\n".join([f"- {warning}" for warning in warnings])
        print(
            f"Warnings when loading configuration file ({config_file}):\n{warning_items}"
        )

    if errors:
        error_items = "\n".join([f"- {error}" for error in errors])
        error_message = (
            f"Errors loading configuration file ({config_file}):\n{error_items}"
        )
        raise ConfigurationError(error_message)

    return configuration


def save_config(config_file: str, configuration: InfestorConfiguration) -> None:
    with atomic_write(config_file, overwrite=True) as ofp:
        json.dump(asdict(configuration), ofp)


def default_config_file(root_directory) -> str:
    config_file = os.path.join(root_directory, CONFIG_FILENAME)

    return config_file


def set_reporter_token(config_file: str, reporter_token: str) -> Dict[str, str]:
    config = load_config(config_file)
    config.reporter_token = reporter_token
    save_config(config_file, config)
    return config


def initialize(
    repository: str,
    python_root: str,
    relative_imports: bool = False,
    reporter_token: Optional[str] = None,
) -> None:
    """
    Initialize infestor in a given project.
    """
    config_file = default_config_file(repository)
    if os.path.exists(config_file):
        raise ConfigurationError(
            f"Pre-existing infestor configuration found: {config_file}"
        )

    configuration = InfestorConfiguration(
        python_root=python_root,
        relative_imports=relative_imports,
        reporter_token=reporter_token,
    )
    save_config(config_file, configuration)
