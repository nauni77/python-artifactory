from __future__ import annotations

import logging

import pytest

from pyartifactory import Artifactory
from pyartifactory.exception import UserNotFoundError, GroupNotFoundError, RepositoryNotFoundError
from pyartifactory.tests.data.data import TestData
from pyartifactory.tests.base_test_real import TestBaseReal


class TestDataReal(TestBaseReal):
    """
    Test modify permissions in artifactory by using API.
    API reference: https://docs.jfrog.com/administration/reference/createpermission

    # permission_details.name -> the name of the permission
    # permission_details.repo.repositories -> contains a list of repositories that the permission applies to
    # permission_details.repo.actions.groups -> contains a list of groups that the permission applies to
    # permission_details.repo.actions.users -> contains a list of users that the permission applies to
    #     -> users and groups have entries of selected enums: PermissionEnumV2.read, ...annotate, ...write, ... delete, ...
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logger.info("setting up the test class for TestDataReal")
        cls.logger = logging.getLogger("pyartifactory_data_real")
        cls._client: Artifactory = TestDataReal.CLIENT_DEFAULT

    @pytest.mark.order(1)
    def test_01_create_users(self) -> None:
        TestData.create_users(self._client)
        try:
            self._client.users.get(TestData.TEST_USERS[0].username)
        except UserNotFoundError:
            self.fail(f"User '{TestData.TEST_USERS[0].username}' was not created successfully.")

    @pytest.mark.order(5)
    def test_05_create_groups(self) -> None:
        # test user is created in the previous test, so we can use this for group creation
        TestData.create_groups(self._client)
        try:
            self._client.groups.get(TestData.TEST_GROUPS[0].name)
        except GroupNotFoundError:
            self.fail(f"Group '{TestData.TEST_GROUPS[0].name}' was not created successfully.")


    @pytest.mark.order(10)
    def test_10_create_repositories(self) -> None:
        TestData.create_repositories(self._client)
        for cur_repo in TestData.TEST_REPOSITORIES_LOCAL:
            try:
                self._client.repositories.get_repo(cur_repo.name)
                self.logger.info(f"Repository '{cur_repo.name}' exists - success.")
            except RepositoryNotFoundError:
                self.fail(f"Repository '{cur_repo.name}' was not created successfully.")

    @pytest.mark.order(15)
    def test_15_create_permissions(self) -> None:
        TestData.create_permissions(self._client)
        # TODO: check results and steps on the way


    @pytest.mark.order(50)
    @pytest.mark.skip(reason="just check creation first - test cleanup after correct creation")
    def test_20_cleanup_all(self) -> None:
        # everything is created in the previous tests, so we can cleanup everything now
        TestData.cleanup(self._client)

        # check for test users
        try:
            self._client.users.get(TestData.TEST_USERS[0].username)
            self.fail(f"User '{TestData.TEST_USERS[0].username}' was not deleted successfully.")
        except UserNotFoundError:
            pass

        # check for test groups
        try:
            self._client.groups.get(TestData.TEST_GROUPS[0].name)
            self.fail(f"Group '{TestData.TEST_GROUPS[0].name}' was not deleted successfully.")
        except GroupNotFoundError:
            pass