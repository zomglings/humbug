"""
These are the tools infestor uses to set up a code base for automatic Humbug instrumentation.
"""
import json
import os
from typing import Dict, Optional

from atomicwrites import atomic_write
from humbug.consent import HumbugConsent, yes, no
from humbug.report import HumbugReporter

CONFIG_FILENAME = "infestor.json"
REPORTER_TOKEN_KEY = "reporter_token"
HUMBUG_CONSENT_KEY = "reporting_consent"


class ConfigurationError(Exception):
    """
    Raised if there is an issue with an infestor configuration file.
    """

    pass


def load_config(config_file: str, validate: bool = True) -> Dict[str, str]:
    """
    Loads an infestor configuration from file and validates it.
    """
    try:
        with open(config_file, "r") as ifp:
            config = json.load(ifp)
    except:
        raise ConfigurationError(f"Could not read configuration: {config_file}")

    if validate:
        if config.get(REPORTER_TOKEN_KEY) is not None:
            raise ConfigurationError(
                f"No reporter token found in configuration file: {config_file}"
            )

    return config


def save_config(config_file: str, config: Dict[str, str]) -> None:
    with atomic_write(config_file, overwrite=True) as ofp:
        json.dump(config, ofp)


def default_config_file(
    root_directory: Optional[str] = None, create: bool = False
) -> str:
    if root_directory is None:
        root_directory = os.getcwd()

    config_file = os.path.join(root_directory, CONFIG_FILENAME)

    if create:
        if not os.path.exists(config_file):
            save_config(config_file, {})
        elif not os.path.isfile(config_file):
            raise ConfigurationError(f"Not a file: {config_file}")
        else:
            load_config(config_file, validate=False)

    return config_file


def set_reporter_token(config_file: str, reporter_token: str) -> None:
    config = load_config(config_file, validate=False)
    config[REPORTER_TOKEN_KEY] = reporter_token
    save_config(config_file, config)


def set_reporting_consent(config_file: str, reporting_consent: bool) -> None:
    config = load_config(config_file, validate=False)
    if reporting_consent:
        config[HUMBUG_CONSENT_KEY] = yes[0]
    else:
        config[HUMBUG_CONSENT_KEY] = no[0]
    save_config(config_file, config)


def initialize(
    repository: Optional[str] = None,
    reporter_token: Optional[str] = None,
) -> None:
    """
    Initialize infestor in a given project.
    """
    config_file = default_config_file(repository, create=False)
    if os.path.exists(config_file):
        raise ConfigurationError(
            f"Pre-existing infestor configuration found: {config_file}"
        )

    config = {HUMBUG_CONSENT_KEY: yes[0]}
    if reporter_token is not None:
        config[REPORTER_TOKEN_KEY] = reporter_token

    save_config(config_file, config)
