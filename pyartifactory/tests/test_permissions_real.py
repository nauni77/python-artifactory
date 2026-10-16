from __future__ import annotations

import logging
import unittest

import pytest

from pyartifactory import Artifactory
from pyartifactory.exception import PermissionNotFoundError
from pyartifactory.helper.permission import clean_permission
from pyartifactory.models import SimplePermission, PermissionV2
from pyartifactory.models.permission import PrincipalsPermissionV2, RepoV2
from pyartifactory.tests.base_test_real import TestBaseReal
from pyartifactory.tests.data.data import TestData


class TestPermissionsReal(TestBaseReal):
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
        cls.logger.info("setting up the test class for TestGroupReal")
        cls.logger = logging.getLogger("pyartifactory_group_real")
        cls._client: Artifactory = TestPermissionsReal.CLIENT_DEFAULT

        TestData.create_repositories(cls._client)
        TestData.create_users(cls._client)
        TestData.create_groups(cls._client)

    def tearDown(self) -> None:
        self.logger.info("tearing down after each test case in TestPermissionsReal")
        super().tearDown()
        TestData.cleanup_permissions(self._client)

    @pytest.mark.order(1)
    def test_01_get_permissions_list_and_details(self) -> None:
        all_permissions: list[SimplePermission] = self._client.permissions.list()
        self.logger.info(f"found permissions: {len(all_permissions)}")
        self.assertGreaterEqual(len(all_permissions), 2)

        for cur_permission in all_permissions:
            permission_details = self._client.permissions.get(cur_permission.name)
            self.logger.info(f"permission details for '{cur_permission.name}': {permission_details}")

    @pytest.mark.order(5)
    def test_05_create_update_test_permission(self) -> None:
        """
        Test creating a new permission in artifactory.
        This depends on creating at least first a user, group and repository from test data definition!
        """
        cur_permission_test_data = TestData.TEST_PERMISSIONS[0]

        self.assertFalse(self._client.permissions.exists(cur_permission_test_data.name),
                         "Permission should not exist now")

        try:
            self._client.permissions.get(cur_permission_test_data.name)
            self.fail("Permission already exists, cannot create it again.")
        except PermissionNotFoundError:
            ...

        actions: PrincipalsPermissionV2 = PrincipalsPermissionV2(
            users=cur_permission_test_data.principals_user,
            groups=cur_permission_test_data.principals_group
        )
        repos: RepoV2 = RepoV2(repositories=cur_permission_test_data.repositories, actions=actions)
        permission: PermissionV2 = PermissionV2(name=cur_permission_test_data.name, repo=repos)
        self._client.permissions.create(permission)

        self.assertTrue(self._client.permissions.exists(cur_permission_test_data.name),
                        "Permission should exist now")

        try:
            self._client.permissions.get(cur_permission_test_data.name)
            self.assertEqual(cur_permission_test_data.name, permission.name)
            self.assertEqual(len(cur_permission_test_data.repositories), [] if permission.repo is None else len(permission.repo.repositories))
        except PermissionNotFoundError:
            self.fail("Permission should exist now!")

        # ATTENTION:
        # This is not working as expected - rename creates a second permission with the new name,
        # but does not delete the old one. Reason is, it's the same API endpoint for update and create!
        details_permission = self._client.permissions.get(cur_permission_test_data.name)
        number_repositories_orig = len(details_permission.repo.repositories)
        details_permission.repo.repositories.pop()

        self._client.permissions.update(details_permission)
        details_permission_after_update = self._client.permissions.get(details_permission.name)

        self.assertEqual(len(details_permission_after_update.repo.repositories), number_repositories_orig - 1,
                         "Permission should have one less repository after update.")


    @pytest.mark.order(20)
    @pytest.mark.skip(reason="It's working ... just for manual testing of copying permissions from one artifactory to another")
    def test_20_copy_permission(self) -> None:
        """
        Test copying a permission from one artifactory to another.
        """
        source_client = self.CLIENT_SOURCE
        target_client = self.CLIENT_TARGET

        source_permission_name = "VSA full permission"
        target_permission_name = "vsa"

        # Get the permission details from the source artifactory
        permission_details_src = source_client.permissions.get(source_permission_name)
        self.logger.info(f"permission details for '{source_permission_name}': {permission_details_src}")

        # # COPY is not needed, just the migration_daemon does not exist on target artifactory
        # actions: PrincipalsPermissionV2 = PrincipalsPermissionV2(
        #     users=permission_details_src.repo.actions.users,
        #     groups=permission_details_src.repo.actions.groups
        # )
        # repos: RepoV2 = RepoV2(repositories=permission_details_src.repo.repositories, actions=actions)
        # new_permission_copy: PermissionV2 = PermissionV2(name=permission_details_src.name, repo=repos)
        # new_permission_copy.name = target_permission_name

        # TODO: Check if include and exclude changed in src permission, and copy them if they exist

        permission_details_src.name = "other_name"

        self.logger.info(f"permission src:\n{permission_details_src.model_dump_json(by_alias=True, exclude_none=True, indent=2)}")
        # self.logger.info(f"permission copy:\n{new_permission_copy.model_dump_json(by_alias=True, exclude_none=True, indent=2)}")

        for cur in target_client.permissions.list():
            self.logger.info(f"Existing permission on target: {cur.name}")

        ## The SRC permission says it already exists! I don't know why ...
        clean_permission(target_client, permission_details_src)
        target_client.permissions.create(permission_details_src)
        # clean_permission(target_client, new_permission_copy)
        # target_client.permissions.create(new_permission_copy)





if __name__ == '__main__':
  unittest.main()