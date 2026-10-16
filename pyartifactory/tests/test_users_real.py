from __future__ import annotations

import unittest

import pytest
from pydantic import EmailStr, SecretStr

from pyartifactory import Artifactory
from pyartifactory.exception import UserAlreadyExistsError, UserNotFoundError
from pyartifactory.models import SimpleUser, NewUser, UserDetails
from pyartifactory.models.user import UserUpdateParamKeysEnum
from pyartifactory.tests.base_test_real import TestBaseReal
from pyartifactory.tests.data.data import TestData

import logging

class TestUsersReal(TestBaseReal):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logger.info("setting up the test class for TestSystemBaseReal")
        cls.logger = logging.getLogger("pyartifactory_users_real")

    @pytest.mark.order(1)
    def test_01_get_user_list(self) -> None:
        """
        This works on new artifactory and at the old API
        """

        user_list: list[SimpleUser] = self.CLIENT_DEFAULT.users.list()
        self.assertGreater(len(user_list), 0, "user list 02 is empty")
        self.logger.info(f"found users -> 02: {len(user_list)}")

        for cur in user_list:
            if cur.username.lower() == TestData.TEST_USERS[0]:
                self.logger.info(f"found '{TestData.TEST_USERS[0]}' in 02: {cur}")


    @pytest.mark.order(10)
    def test_10_get_user_detail(self):
        # admin should always exist in Artifactory, so we can use it for testing
        user_detail_admin: UserDetails = self.CLIENT_DEFAULT.users.get("anonymous")
        self.assertIsNotNone(user_detail_admin)

    @pytest.mark.order(20)
    def test_20_delete_create_local_user(self) -> None:

        client: Artifactory = TestUsersReal.CLIENT_DEFAULT

        new_user: NewUser = NewUser(
            username=TestData.TEST_USERS[0].username,
            password=SecretStr(TestData.TEST_USERS[0].password),
            email=TestData.TEST_USERS[0].email)

        username = new_user.username
        self.logger.info(f"add user {username}")
        try:
            client.users.create(new_user)
        except UserAlreadyExistsError as e:
            self.logger.info(f"found user {username} - delete it first")
            client.users.delete(new_user.username)
            self.logger.info(f"found user {username} - delete it first - DONE!")
            self.logger.info(f"add user {username} - retry")
            client.users.create(new_user)
        self.logger.info(f"add user {username} - DONE!")

    @pytest.mark.order(30)
    def test_30_update_local_user(self) -> None:

        # at old Artifactory this is not working, only at new Artifactory
        client: Artifactory = TestUsersReal.CLIENT_DEFAULT

        username: str = TestData.TEST_USERS[0].username
        changed_email: EmailStr = "tester.email.changed@company.de"

        try:
            self.logger.info(f"try to get user {username}")
            client.users.get(username)
            self.logger.info(f"found user {TestData.TEST_USERS[0]} - delete existing first")
            client.users.delete(username)
            self.logger.info(f"user {TestData.TEST_USERS[0]} - deleted")
        except UserNotFoundError:
            pass

        self.logger.info(f"create test user: {TestData.TEST_USERS[0]}")
        new_user: NewUser = NewUser(
            username=username,
            password=SecretStr(TestData.TEST_USERS[0].password),
            email=TestData.TEST_USERS[0].email,
            admin=False)

        client.users.create(new_user)
        self.logger.info(f"create test user: {TestData.TEST_USERS[0]} - DONE!")
        self.logger.info(f"try to get user {TestData.TEST_USERS[0]} again")
        my_user: UserDetails = client.users.get(username)
        self.assertEqual(username, my_user.username)
        self.assertNotEqual(my_user.email, changed_email)
        my_user.email = changed_email

        # just update email of user
        my_user_changed: UserDetails = client.users.update_partial(username, {UserUpdateParamKeysEnum.email: changed_email})
        self.assertEqual(my_user_changed.email, changed_email)
        self.logger.info(f"update user {my_user.username}")

        # update again with another mail address
        another_changed_email: EmailStr = "another.email.changed@company.de"
        my_user_changed.email = another_changed_email

        # TODO: ATTENTION: this works only with Artifactory 7.128.0 and newer. Activate after update our Artifactory.
        # second_change: UserDetails = client.users.update(username, my_user_changed)
        # self.assertEqual(second_change.email, another_changed_email,
        #                  "result from update with user_details_obj, email does not match")
        # self.logger.info(f"update user {my_user.username} - DONE!")

    @pytest.mark.order(50)
    @unittest.skip("This only works with a locked user - but I can't find a way to lock a user in real.")
    def test_50_unlock_local_user(self) -> None:
        """
        Usually a user should be locked after X failed login attempts.
        But I can't find a way to lock a user in real.
        Because of this the test is skipped.
        """
        username = TestData.TEST_USERS[0].username
        self.logger.info(f"unlock user {username}")
        TestUsersReal.CLIENT_DEFAULT.users.unlock(username)
        self.logger.info(f"unlock user {username} - DONE!")

if __name__ == '__main__':
  unittest.main()