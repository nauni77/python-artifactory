from __future__ import annotations

import logging
import unittest

from pyartifactory.models.system import StorageInfo
from pyartifactory.tests.base_test_real import TestBaseReal


class TestSystemReal(TestBaseReal):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logger.info("setting up the test class for TestSystemBaseReal")
        cls.logger = logging.getLogger("pyartifactory_system_real")

    def test_artifactory_ping(self):
        """
        This test checks if the Artifactory instance is alive by sending a ping request.
        It can also be used to log in with an LDAP-user to make this user visible at Artifactory.
        """
        ping_result: bool = TestSystemReal.CLIENT_DEFAULT.system.artifactory_ping()
        self.logger.info(f"Artifactory ping result: {ping_result}")
        self.assertTrue(ping_result)

    def test_readiness_probe(self):
        readiness_result: bool = TestSystemReal.CLIENT_DEFAULT.system.readiness_probe()
        self.logger.info(f"Artifactory readiness probe result: {readiness_result}")
        self.assertTrue(readiness_result)

    def test_liveness_probe(self):
        liveness_result: bool = TestSystemReal.CLIENT_DEFAULT.system.liveness_probe()
        self.logger.info(f"Artifactory liveness probe result: {liveness_result}")
        self.assertTrue(liveness_result)

    def test_get_artifactory_version(self):
        version: str = TestSystemReal.CLIENT_DEFAULT.system.get_artifactory_version()
        self.logger.info(f"Artifactory version: {version}")
        self.assertIsNotNone(version, "no version information received from Artifactory")

    def test_get_system_info(self):
        system_info: str = TestSystemReal.CLIENT_DEFAULT.system.get_system_info()
        self.logger.info(f"Artifactory system info: \n{system_info}")
        self.assertTrue(system_info is not None and len(system_info) > 0)


    def test_get_license_information(self):
        license_info: str = TestSystemReal.CLIENT_DEFAULT.system.get_license_information()
        self.logger.info(f"Artifactory license information: \n{license_info}")
        self.assertTrue(license_info is not None and len(license_info) > 0)

    # @unittest.skip("This test is only for an Admin to log the license information of all Artifactories.")
    def test_show_license_information_all_clients(self):
        self.logger.info(f"artifactory license information: {TestSystemReal.CLIENT_DEFAULT.system.get_license_information()}")

    def test_get_background_tasks(self):
        self.logger.info(f"artifactory background tasks:")
        result: list[dict[str, str]] = TestSystemReal.CLIENT_DEFAULT.system.get_background_tasks()
        for cur in result['tasks']:
            self.logger.info(f"background task: {cur}")

    def test_get_storage_summary_info(self) -> None:
        storage_summary_info: StorageInfo = TestSystemReal.CLIENT_DEFAULT.system.get_storage_summary_info()
        self.logger.info(f"Artifactory storage summary information: \n{storage_summary_info}")
        self.assertTrue(storage_summary_info is not None and len(storage_summary_info.repositories_summary_list) > 0)

    def test_refresh_storage_summary_info(self) -> None:
        refresh_result = TestSystemReal.CLIENT_DEFAULT.system.refresh_storage_summary_info()
        self.logger.info(f"Artifactory refresh storage summary information result: {refresh_result}")
        self.assertTrue(refresh_result)

if __name__ == '__main__':
  unittest.main()