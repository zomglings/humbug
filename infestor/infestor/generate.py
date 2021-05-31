import ast
import logging
import os
from typing import List, Optional

from .config import (
    InfestorConfiguration,
    default_config_file,
    load_config,
    save_config,
)

DEFAULT_REPORTER_FILENAME = "report.py"
REPORTER_FILE_TEMPLATE: Optional[str] = None
TEMPLATE_FILEPATH = os.path.join(os.path.dirname(__file__), "report.py.template")
try:
    with open(TEMPLATE_FILEPATH, "r") as ifp:
        REPORTER_FILE_TEMPLATE = ifp.read()
except Exception as e:
    logging.warn(f"WARNING: Could not load reporter template from {TEMPLATE_FILEPATH}:")
    logging.warn(e)


class GenerateReporterError(Exception):
    pass


def setup_system_report(
    repository: str, python_root: str, reporter_filepath: str
) -> None:
    # TODO(zomglings): What if python_root is a file and reporter_filepath is not in the same
    # directory as that file? For now, this case has been half-assed here.
    config_file = default_config_file(repository)
    configuration = load_config(config_file).get(python_root)
    if configuration is None:
        raise GenerateReporterError(
            f"Could not find Python root ({python_root}) in configuration file ({config_file})"
        )
    target_file = os.path.join(repository, python_root)
    if os.path.isdir(target_file):
        target_file = os.path.join(target_file, "__init__.py")
        if not os.path.exists(target_file):
            with open(target_file, "w") as ofp:
                ofp.write("")

    module: Optional[ast.Module] = None
    with open(target_file, "r") as ifp:
        module = ast.parse(ifp.read())

    last_import_line_number = 0
    for statement in module.body:
        if isinstance(statement, ast.Import) or isinstance(statement, ast.ImportFrom):
            last_import_line_number = statement.lineno

    # TODO(zomglings): Create an AST node which imports the reporter and runs reporter.system_report()
    path_to_reporter_file = os.path.relpath(
        os.path.join(repository, python_root, reporter_filepath),
        os.path.dirname(target_file),
    )
    path_components: List[str] = []
    current_path = path_to_reporter_file
    while current_path:
        current_path, base = os.path.split(current_path)
        if base == os.path.basename(reporter_filepath):
            base, _ = os.path.splitext(base)
        path_components = [base] + path_components

    source_lines: List[str] = []
    with open(target_file, "r") as ifp:
        for line in ifp:
            source_lines.append(line)

    new_code = ""
    if not configuration.relative_imports:
        path_components = [os.path.basename(python_root)] + path_components
        name = ".".join(path_components)
        new_code = f"import {name}\n{name}.reporter.system_report()\n"
    else:
        name = ".".join(path_components)
        new_code = f"from .{name} import reporter\nreporter.system_report()\n"

    source_lines = (
        source_lines[:last_import_line_number]
        + [new_code]
        + source_lines[last_import_line_number:]
    )

    with open(target_file, "w") as ofp:
        for line in source_lines:
            ofp.write(line)


def setup_reporter(
    repository: str,
    python_root: str,
    reporter_filepath: Optional[str],
    auto_system_report: bool = False,
) -> None:
    if REPORTER_FILE_TEMPLATE is None:
        raise GenerateReporterError("Could not load reporter template file")

    config_file = default_config_file(repository)
    configurations_by_python_root = load_config(config_file)

    configuration = configurations_by_python_root.get(python_root)
    if configuration is None:
        raise GenerateReporterError(
            f"Could not find configuration for python root ({python_root}) in config file ({config_file})"
        )

    if reporter_filepath is None:
        if configuration.reporter_filepath is not None:
            reporter_filepath = configuration.reporter_filepath
        else:
            reporter_filepath = DEFAULT_REPORTER_FILENAME
    else:
        if (
            configuration.reporter_filepath is not None
            and configuration.reporter_filepath != reporter_filepath
        ):
            raise GenerateReporterError(
                f"Configuration expects reporter to be set up at a different file than the one specified; specified={reporter_filepath}, expected={configuration.reporter_filepath}"
            )

    reporter_filepath_full = os.path.join(
        repository, configuration.python_root, reporter_filepath
    )
    if os.path.exists(reporter_filepath_full):
        raise GenerateReporterError(
            f"Object already exists at desired reporter filepath: {reporter_filepath_full}"
        )

    if configuration.reporter_token is None:
        raise GenerateReporterError("No reporter token was specified in configuration")

    contents = REPORTER_FILE_TEMPLATE.format(
        project_name=configuration.project_name,
        reporter_token=configuration.reporter_token,
    )
    with open(reporter_filepath_full, "w") as ofp:
        ofp.write(contents)

    setup_system_report(repository, python_root, reporter_filepath)

    configuration.reporter_filepath = reporter_filepath
    save_config(config_file, configuration)
