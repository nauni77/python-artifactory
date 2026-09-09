from __future__ import annotations

import logging
from typing import List, Union

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, UserAlreadyExistsError, UserNotFoundError
from pyartifactory.models.user import NewUser, SimpleUser, UserDetails
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryUser(ArtifactoryObject):
    """
    Manipulate an artifactory user
    API details: https://docs.jfrog.com/administration/reference/getuserdetails

    Mabe useful will be:
    - Add or remove users from groups:
      https://docs.jfrog.com/administration/reference/updateusergroups
    - Change a user password
      https://docs.jfrog.com/administration/reference/changeuserpassword
    """
    _uri_v2 = "access/api/v2/users"

    def create(self, user: NewUser) -> UserDetails:
        """
        Create user
        API details: https://docs.jfrog.com/administration/reference/createuser

        :param user: NewUser object
        :return: User
        """
        username = user.username

        try:
            self.get(username)
        except UserNotFoundError:
            # This should happen, because the user should not exist yet.
            # We can proceed to create the user. Executing the creation of the user at except block
            # will cause to hide the reason of the failure if the creation fails.
            # So we just pass here and continue to create the user.
            pass
        else:
            logger.error("User %s already exists", username)
            raise UserAlreadyExistsError(f"User {username} already exists")

        data = user.model_dump(exclude_none=True)
        data["password"] = user.password.get_secret_value()
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        self._post(f"{self._uri_v2}", headers=headers, json=data)

        logger.debug("User %s successfully created", username)
        return self.get(username)


    def get(self, name: str) -> UserDetails:
        """
        Read user from artifactory. Fill object if existed.
        API: https://docs.jfrog.com/administration/reference/getuserdetails

        :param name: Name of the user to retrieve
        :return: UserModel
        """
        try:
            response = self._get(f"{self._uri_v2}/{name}")
            logger.debug("User %s found", name)
            return UserDetails(**response.json())
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("User %s does not exist", name)
                raise UserNotFoundError(f"{name} does not exist")
            raise ArtifactoryError from error

    def list(self) -> List[SimpleUser]:
        """
        Lists all the users
        API: https://docs.jfrog.com/administration/reference/getuserlist

        :return: UserList
        """
        response = self._get(route=f"{self._uri_v2}", headers={"accept": "application/json"})
        logger.debug("List all users successful")
        return [SimpleUser(**user) for user in response.json().get("users", [])]

    def update_partial(self, username: str, data: dict[str, object]) -> UserDetails:
        """
        Updates an artifactory user
        API: https://docs.jfrog.com/administration/reference/updateuser

        All fields are optional;
        if a specific field is not specified the value will not change.
        Only put the data you want to change in the request body.

        Attention: Groups are not supported during this update!

        During an update the password only needs to be provided,
        if the 'internal_password_disabled' changes from True to False.

        :param username: username of the user to update
        :param data: Dictionary of values to update
        :return: UserDetails
        """
        username = username

        # check if user exists, if not raise UserNotFoundError
        self.get(username)

        data = data

        # define application/json for the request
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        logger.info(f"update existing user {username} with values: {data}")

        self._patch(
            f"{self._uri_v2}/{username}",
            headers=headers,
            json=data,
        )

        logger.debug("User %s successfully updated", username)
        return self.get(username)

    def update(self, username: str, data: UserDetails) -> UserDetails:
        """
        This works only with Artifactory 7.128.0 and newer.
        Use as update_partial, but with a UserDetails object instead of a dictionary.
        API: https://docs.jfrog.com/administration/reference/updateuser

        :param username: username of the user to update
        :param data: User object
        :return: UserDetails
        """
        values = data.model_dump(exclude_none=True, exclude={"last_logged_in", "groups", "status", "realm"}) if data is not None else {}
        return self.update_partial(username, values)

    def delete(self, username: str) -> None:
        """
        Delete user
        API: https://docs.jfrog.com/administration/reference/deleteuser

        :param username: Name of the user to delete
        :return: None
        """
        self.get(username)
        self._delete(f"{self._uri_v2 }/{username}")
        logger.debug("User %s successfully deleted", username)

    def unlock(self, name: str) -> None:
        """
        Unlock user
        API: https://docs.jfrog.com/administration/reference/unlockuser

        :param name: Name of the user to unlock
        :return none
        """
        # curl --request POST \
        #      --url https://trepo.intra.vsa.de/access/api/v2/users/py_test_user/unlock \
        #      --header 'authorization: Bearer my_token'
        self._post(f"{self._uri_v2}/{name}/unlock")
        logger.debug("User % successfully unlocked", name)
