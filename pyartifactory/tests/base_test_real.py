from __future__ import annotations

import logging
import os
import unittest

from pyartifactory import Artifactory
from pyartifactory.tests.data.data import TestAuthConfig


class TestBaseReal(unittest.TestCase):

    # TODO: Just use two for source and target - with fitting env variables for everybody

    # TEST CLIENTS to access our Artifactory instances, with different users and permissions.
    TEST_01_ADMIN: TestAuthConfig = TestAuthConfig(
        url="https://vpartifactory01-x.intra.vsa.de",
        bearer_token=os.environ["ARTIFACTORY_01_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_01_ADMIN_PASSWORD"],
    )

    # TEST_02_ADMIN: TestAuthConfig = TestAuthConfig(
    #     url="https://vpartifactory02-x.intra.vsa.de",
    #     bearer_token=os.environ["ARTIFACTORY_02_ADMIN_BEARER_TOKEN"],
    #     username="admin",
    #     password=os.environ["ARTIFACTORY_02_ADMIN_PASSWORD"],
    # )

    TEST_03_ADMIN: TestAuthConfig = TestAuthConfig(
        url="https://vpartifactory03-x.intra.noventigroup.com",
        bearer_token=os.environ["ARTIFACTORY_03_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_03_ADMIN_PASSWORD"],
    )

    TEST_04_ADMIN: TestAuthConfig = TestAuthConfig(
        url="https://vpartifactory04-x.intra.noventigroup.com",
        bearer_token=os.environ["ARTIFACTORY_04_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_04_ADMIN_PASSWORD"],
    )

    TEST_03_CIAM_BUILD: TestAuthConfig = TestAuthConfig(
        url="https://vpartifactory03-x.intra.noventigroup.com",
        bearer_token=os.environ["ARTIFACTORY_03_ADMIN_BEARER_TOKEN"],
        username="admin",
        password=os.environ["ARTIFACTORY_03_ADMIN_PASSWORD"],
    )

    TEST_03_ANSIBLE_ENTW_BUILD: TestAuthConfig = TestAuthConfig(
        url="https://vpartifactory03-x.intra.noventigroup.com",
        bearer_token=os.environ["ARTIFACTORY_03_ADMIN_BEARER_TOKEN"],
        username="ansibleEntwBuild",
        password=os.environ["ARTIFACTORY_ANSIBLE_ENTW_PASSWORD"],
    )

    TEST_FRA_ADMIN: TestAuthConfig = TestAuthConfig(
        url="https://vpartifactory01-20.intra.noventigroup.com",
        bearer_token=os.environ["ARTIFACTORY_FRA_ADMIN_BEARER_TOKEN"],
        username="admin",
        password="UNSET",
    )


    @classmethod
    def setUpClass(cls):
        """
        This method is called before any tests in the class are run.
        The first parameter is the class itself, not self.
        """

        cls.logger = logging.getLogger("pyartifactory_real")
        cls.logger.info("setting up the test class")

        # TODO: maybe migrate this also to simple dict,
        #       like TEST_USER, TEST_GROUP, TEST_LOCAL_REPOSITORIES, TEST_REMOTE_REPOSITORIES,
        #       TEST_VIRTUAL_REPOSITORIES, TEST_PERMISSIONS

        cls.TEST: TestAuthConfig = cls.TEST_03_ADMIN

        cls.CLIENT_01: Artifactory = Artifactory(url=cls.TEST_01_ADMIN.url,
                                                 access_token=cls.TEST_01_ADMIN.bearer_token)
        # cls.CLIENT_02: Artifactory = Artifactory(url=cls.TEST_02_ADMIN.url,
        #                                          access_token=cls.TEST_02_ADMIN.bearer_token)
        cls.CLIENT_03: Artifactory = Artifactory(url=cls.TEST_03_ADMIN.url,
                                                 access_token=cls.TEST_03_ADMIN.bearer_token)
        cls.CLIENT_04: Artifactory = Artifactory(url=cls.TEST_04_ADMIN.url,
                                                 access_token=cls.TEST_04_ADMIN.bearer_token)
        cls.CLIENT_FRA: Artifactory = Artifactory(url=cls.TEST_FRA_ADMIN.url,
                                                 access_token=cls.TEST_FRA_ADMIN.bearer_token)

        cls.CLIENT_DEFAULT: Artifactory = cls.CLIENT_03

    @classmethod
    def tearDownClass(cls):
        """
        This method is called after all tests in the class have run.
        The first parameter is the class itself, not self.
        """
        cls.logger.info("cleanup test data after all tests in the class have run")
        # TODO: enable later if everything works fine, but for now we want to keep the test data for manual testing
        # TestData.cleanup(cls.CLIENT_DEFAULT)
        cls.logger.info("tearing down the test class")




