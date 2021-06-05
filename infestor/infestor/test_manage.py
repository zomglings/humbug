import json
import os
import shutil
import sys
import tempfile
import unittest
import uuid

from . import config, manage


class TestSetupReporter(unittest.TestCase):
    def setUp(self):
        self.repository = tempfile.mkdtemp()

        self.fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")

        script_basename = "a_script.py"
        script_file_fixture = os.path.join(self.fixtures_dir, script_basename)
        self.script_file = os.path.join(self.repository, script_basename)
        shutil.copyfile(script_file_fixture, self.script_file)

        package_basename = "a_package"
        package_dir_fixture = os.path.join(self.fixtures_dir, package_basename)
        self.package_dir = os.path.join(self.repository, package_basename)
        shutil.copytree(package_dir_fixture, self.package_dir)

        self.reporter_token = str(uuid.uuid4())

    def tearDown(self) -> None:
        DEBUG = os.getenv("DEBUG")
        if DEBUG != "1":
            shutil.rmtree(self.repository)
        else:
            print(
                f"DEBUG=1: Retaining test directory - {self.repository}",
                file=sys.stderr,
            )

    def test_setup_for_package(self):
        config.initialize(
            self.repository,
            self.package_dir,
            "a_package",
            reporter_token=self.reporter_token,
        )
        self.assertTrue(
            os.path.exists(os.path.join(self.repository, config.CONFIG_FILENAME))
        )

        manage.add_reporter(self.repository, self.package_dir)

        infestor_json_path = config.default_config_file(self.repository)
        self.assertTrue(os.path.exists(infestor_json_path))
        with open(infestor_json_path, "r") as ifp:
            infestor_json = json.load(ifp)

        expected_config_json = {
            "a_package": {
                "python_root": "a_package",
                "project_name": "a_package",
                "relative_imports": False,
                "reporter_token": self.reporter_token,
                "reporter_filepath": "report.py",
            }
        }
        self.assertDictEqual(infestor_json, expected_config_json)

        self.assertTrue(
            os.path.exists(
                os.path.join(
                    self.repository,
                    self.package_dir,
                    "report.py",
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
