from __future__ import annotations

import logging
import unittest
from typing import List

import pytest
from pydantic import SecretStr

from pyartifactory.exception import GroupNotFoundError, UserNotFoundError
from pyartifactory.models import UserDetails, NewUser
from pyartifactory.models.group import SimpleGroup, GroupDetails, NewGroup, GroupUpdateParamKeysEnum
from pyartifactory.objects.artifactory import Artifactory
from pyartifactory.tests.base_test_real import TestBaseReal
from pyartifactory.tests.data.data import TestData



class TestGroupsReal(TestBaseReal):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logger.info("setting up the test class for TestGroupReal")
        cls.logger = logging.getLogger("pyartifactory_group_real")
        cls._client: Artifactory = TestGroupsReal.CLIENT_DEFAULT

    @pytest.mark.order(1)
    def test_get_groups_list(self) -> None:

        all_groups: List[SimpleGroup] = self._client.groups.list()
        for cur in all_groups:
            self.logger.info(f"found group: {cur.group_name} -> {cur}")

        self.assertGreater(len(all_groups), 0, "group list is empty")

    @pytest.mark.order(5)
    def test_get_group_details(self) -> None:
        all_groups: List[SimpleGroup] = self._client.groups.list()
        for cur in all_groups:
            group_details: GroupDetails = self._client.groups.get(cur.group_name)
            self.logger.info(f"found group details: {cur.group_name} -> {group_details}")
            self.assertEqual(group_details.name, cur.group_name, "group name does not match")

        try:
         self._client.groups.get("some_non_existing_group")
         self.fail("failed to raise an exception on not existing group")
        except GroupNotFoundError:
            self.logger.info("exception was thrown as expected for non-existing group")

    @pytest.mark.order(10)
    def test_create_delete_group(self) -> None:

        test_group_name = TestData.TEST_GROUPS[0].name
        test_group_description = TestData.TEST_GROUPS[0].description

        # check if group already exists and delete it if it does
        try:
            self._client.groups.get(test_group_name)
            self.logger.info(f"Group {test_group_name} already exists, deleting it for test setup")
            self._client.groups.delete(test_group_name)
            self.logger.info(f"Group {test_group_name} deleted, proceeding with test")
        except GroupNotFoundError:
            self.logger.info(f"Group {test_group_name} does not exist, proceeding with test")

        # Create a new group
        new_group = NewGroup(name=test_group_name, description=test_group_description)
        created_group = self._client.groups.create(new_group)
        self.logger.info(f"Created group: {created_group}")

        # Verify the group was created, retrieve again and check the details
        retrieved_group: GroupDetails = self._client.groups.get(test_group_name)
        self.assertIsNotNone(retrieved_group, "failed to retrieve the created group")
        self.assertEqual(retrieved_group.name, test_group_name, "group name does not match")
        self.assertEqual(retrieved_group.description, test_group_description, "group description does not match")

        # Delete the group
        self._client.groups.delete(test_group_name)
        self.logger.info(f"Deleted group: {test_group_name}")

        # Verify the group was deleted
        with self.assertRaises(GroupNotFoundError):
            self._client.groups.get(test_group_name)


    @pytest.mark.order(20)
    def test_modify_group_description(self) -> None:

        test_group_name = TestData.TEST_GROUPS[0].name
        test_group_description = TestData.TEST_GROUPS[0].description

        # Create a new group for testing
        new_group = NewGroup(name=test_group_name, description=test_group_description)
        try:
            if self._client.groups.get(test_group_name):
                self._client.groups.delete(test_group_name)
                self.logger.info(f"Deleted existing group for modification test: {test_group_name}")
        except GroupNotFoundError:
            self.logger.info(f"Group {test_group_name} does not exist, proceeding with creation for modification test")

        created_group = self._client.groups.create(new_group)
        self.logger.info(f"Created group for modification test: {created_group}")

        description_first_change = "some other description for testing"
        self.assertNotEqual(description_first_change, created_group.description, "new description was changed and should be different from the original")
        updated_group: GroupDetails = self._client.groups.update_partial(group_name=created_group.name,
                                             data={GroupUpdateParamKeysEnum.description: description_first_change})
        self.logger.info(f"Updated group with members: {updated_group}")

        self.assertEqual(description_first_change, updated_group.description, "result from update, group name does not match")

        reloaded_group: GroupDetails = self._client.groups.get(test_group_name)
        self.assertEqual(description_first_change, reloaded_group.description, "result from update, group name does not match")

        description_second_change = "another description for testing"
        reloaded_group.description = description_second_change
        updated_group = self._client.groups.update(group_name=reloaded_group.name, data=reloaded_group)

        self.assertEqual(description_second_change, updated_group.description,
                         "result from update with group_details_obj, group name does not match")
        reloaded_group: GroupDetails = self._client.groups.get(test_group_name)
        self.assertEqual(description_second_change, reloaded_group.description,
                         "result from update with group_details_obj, group name does not match")

        # Clean up by deleting the group
        self._client.groups.delete(test_group_name)
        self.logger.info(f"Deleted test group after modification test: {test_group_name}")


    @pytest.mark.order(30)
    def test_group_add_and_remove_members(self) -> None:

        test_group_name = TestData.TEST_GROUPS[0].name
        test_group_description = TestData.TEST_GROUPS[0].description

        # Create a new group for testing
        new_group = NewGroup(name=test_group_name, description=test_group_description)
        try:
            if self._client.groups.get(test_group_name):
                self._client.groups.delete(test_group_name)
                self.logger.info(f"Deleted existing group for modification test: {test_group_name}")
        except GroupNotFoundError:
            self.logger.info(f"Group {test_group_name} does not exist, proceeding with creation for modification test")

        created_group = self._client.groups.create(new_group)
        self.logger.info(f"Created group for modification test: {created_group}")

        try:
            created_user: UserDetails = self._client.users.get(TestData.TEST_USERS[0].username)
            self.logger.info(f"User {TestData.TEST_USERS[0].username} already exists, deleting it for test setup")
        except UserNotFoundError:
            self.logger.info(f"User {TestData.TEST_USERS[0].username} does not exist, proceeding with creation for modification test")
            created_user: UserDetails = self._client.users.create(user=NewUser(username=TestData.TEST_USERS[0].username,
                                                                         password=SecretStr(TestData.TEST_USERS[0].password),
                                                                         email=TestData.TEST_USERS[0].email))
        self.logger.info(f"Created user for modification test: {created_user}")

        if created_group.members is not None:
            self.assertEqual(0, len(created_group.members), "group should have no members after creation")

        changed_detail: GroupDetails = self._client.groups.modify_group_members(group_name=created_group.name, add=[TestData.TEST_USERS[0].username], remove=[])

        self.assertEqual(changed_detail.members, [TestData.TEST_USERS[0].username], "group members should contain the added user")
        reload_changed_detail: GroupDetails = self._client.groups.get(test_group_name)

        self.assertEqual(reload_changed_detail.members, [TestData.TEST_USERS[0].username], "reload group, group members should contain the added user")
        self._client.groups.modify_group_members(created_group.name, add=[], remove=[TestData.TEST_USERS[0].username])
        reload_changed_detail: GroupDetails = self._client.groups.get(test_group_name)
        if reload_changed_detail.members is not None:
            self.assertEqual(0, len(reload_changed_detail.members), "reload group, group members should be empty after removing the user")

        self._client.users.delete(created_user.username)
        self.logger.info(f"Deleted test user after modification test: {created_user.username}")
        self._client.groups.delete(test_group_name)
        self.logger.info(f"Deleted test group after modification test: {test_group_name}")


if __name__ == '__main__':
  unittest.main()