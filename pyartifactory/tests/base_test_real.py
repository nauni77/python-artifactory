from __future__ import annotations

import logging
import os
import unittest

from pyartifactory import Artifactory
from pyartifactory.tests.data.data import TestAuthConfig, TestData


class TestBaseReal(unittest.TestCase):

    # TEST CLIENTS to access our Artifactory instances, with different users and permissions.
    TEST_ADMIN_SOURCE: TestAuthConfig = TestAuthConfig(
        url=os.environ["ARTIFACTORY_SOURCE_URL"],
        bearer_token=os.environ["ARTIFACTORY_SOURCE_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_SOURCE_ADMIN_PASSWORD"],
    )

    TEST_ADMIN_TARGET: TestAuthConfig = TestAuthConfig(
        url=os.environ["ARTIFACTORY_TARGET_URL"],
        bearer_token=os.environ["ARTIFACTORY_TARGET_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_TARGET_ADMIN_PASSWORD"],
    )

    TEST_ADMIN_DEFAULT: TestAuthConfig = TestAuthConfig(
        url=os.environ["ARTIFACTORY_DEFAULT_URL"],
        bearer_token=os.environ["ARTIFACTORY_DEFAULT_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_DEFAULT_ADMIN_PASSWORD"],
    )

    @classmethod
    def setUpClass(cls):
        """
        This method is called before any tests in the class are run.
        The first parameter is the class itself, not self.
        """

        cls.logger = logging.getLogger("pyartifactory_real")
        cls.logger.info("setting up the test class")

        cls.DEFAULT: TestAuthConfig = cls.TEST_ADMIN_DEFAULT

        cls.CLIENT_SOURCE: Artifactory = Artifactory(url=cls.TEST_ADMIN_SOURCE.url,
                                                     access_token=cls.TEST_ADMIN_SOURCE.bearer_token)
        cls.CLIENT_TARGET: Artifactory = Artifactory(url=cls.TEST_ADMIN_TARGET.url,
                                                     access_token=cls.TEST_ADMIN_TARGET.bearer_token)
        cls.CLIENT_DEFAULT: Artifactory = Artifactory(url=cls.TEST_ADMIN_DEFAULT.url,
                                                 access_token=cls.TEST_ADMIN_DEFAULT.bearer_token)

    @classmethod
    def tearDownClass(cls):
        """
        This method is called after all tests in the class have run.
        The first parameter is the class itself, not self.
        """
        cls.logger.info("cleanup test data after all tests in the class have run")
        TestData.cleanup(cls.CLIENT_DEFAULT)
        cls.logger.info("tearing down the test class")




