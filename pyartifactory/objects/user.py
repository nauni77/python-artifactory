from __future__ import annotations

import logging
from typing import List, Union

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, UserAlreadyExistsError, UserNotFoundError
from pyartifactory.models.user import NewUser, SimpleUser, User, UserResponse
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryUser(ArtifactoryObject):
    """Models an artifactory user."""

    _uri = "security/users"

    def create(self, user: NewUser) -> UserResponse:
        """
        Create user
        :param user: NewUser object
        :return: User
        """
        username = user.name
        try:
            self.get(username)
            logger.error("User %s already exists", username)
            raise UserAlreadyExistsError(f"User {username} already exists")
        except UserNotFoundError:
            data = user.model_dump()
            data["password"] = user.password.get_secret_value()
            self._put(f"artifactory/api/{self._uri}/{username}", json=data)
            logger.debug("User %s successfully created", username)
            return self.get(user.name)

    def get(self, name: str) -> UserResponse:
        """
        Read user from artifactory. Fill object if exist
        Since: 2.4.0 (Requires Artifactory Pro)

        url = "https://{your_repo_uri}/artifactory/api/security/users/userName"
        headers = {
            "accept": "application/json",
            "authorization": "Basic ••••"
        }

        :param name: Name of the user to retrieve
        :return: UserModel
        """
        try:
            response = self._get(f"artifactory/api/{self._uri}/{name}")
            logger.debug("User %s found", name)
            return UserResponse(**response.json())
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("User %s does not exist", name)
                raise UserNotFoundError(f"{name} does not exist")
            raise ArtifactoryError from error

    def list(self) -> List[SimpleUser]:
        """
        Since: 2.4.0
        Note: From Artifactory release 7.49.3,
        this API is being replaced by the new Security APIs available in the JFrog Platform.

        Example:
        url = "https://{your_repo_uri}/access/api/v2/users"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        print(response.text)

        Lists all the users
        :return: UserList
        """
        response = self._get(f"artifactory/api/{self._uri}")
        logger.debug("List all users successful")
        return [SimpleUser(**user) for user in response.json()]

    def update(self, user: User) -> UserResponse:
        """
        Updates an artifactory user
        API: https://docs.jfrog.com/administration/reference/updateuser

        Example:
        url = "https://{your_repo_uri}/access/api/v2/users/username"
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        response = requests.patch(url, headers=headers)
        print(response.text)

        :param user: NewUser object
        :return: UserModel
        """
        username = user.name
        self.get(username)
        self._post(
            f"artifactory/api/{self._uri}/{username}",
            json=user.model_dump(exclude={"lastLoggedIn", "realm"}),
        )
        logger.debug("User %s successfully updated", username)
        return self.get(username)

    def delete(self, name: str) -> None:
        """
        Remove user
        :param name: Name of the user to delete
        :return: None
        """
        self.get(name)
        self._delete(f"artifactory/api/{self._uri}/{name}")
        logger.debug("User %s successfully deleted", name)

    def unlock(self, name: str) -> None:
        """
        Unlock user
        Even if the user doesn't exist, it succeed too
        :param name: Name of the user to unlock
        :return none
        """
        self._post(f"artifactory/api/security/unlockUsers/{name}")
        logger.debug("User % successfully unlocked", name)
