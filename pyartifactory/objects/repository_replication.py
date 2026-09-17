from __future__ import annotations

import logging
from typing import Union, NoReturn

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, BadRequestError, \
    BadCredentialsError, PermissionDeniedError, RepositoryNotFoundError
from pyartifactory.models.repository_replication import ReplicationModel, ReplicationStatusModel
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")

class ArtifactoryRepositoryReplication(ArtifactoryObject):
    """
    Models an artifactory repository replication.
    API reference: https://docs.jfrog.com/artifactory/reference/getrepositoryreplicationconfiguration
    """

    _uri_with_s = "artifactory/api/replications"
    _uri_without_s = "artifactory/api/replication"

    # TODO: move to exceptions -> handle_exception function
    def _handle_exception(self, repo_key: str, error: requests.exceptions.HTTPError) -> NoReturn:
        http_response: Union[Response, None] = error.response
        if isinstance(http_response, Response) and http_response.status_code == 400:
            logger.error(f"Bad Request - Repository not found or invalid key. Repository: {repo_key}")
            raise RepositoryNotFoundError(f"Bad Request - Repository not found or invalid key. Repository: {repo_key}")
        elif isinstance(http_response, Response) and http_response.status_code == 401:
            logger.error(f"Bad Credentials - Authentication failed. A valid token is required. Repository: {repo_key}")
            raise BadCredentialsError(
                f"Bad Credentials - Authentication failed. A valid token is required. Repository: {repo_key}")
        elif isinstance(http_response, Response) and http_response.status_code == 403:
            logger.error(f"Permission Denied - User does not have admin permissions.")
            raise PermissionDeniedError(f"Permission Denied - User does not have admin permissions.")
        elif isinstance(http_response, Response) and http_response.status_code == 404:
            logger.error(f"Not Found - The specified repository does not exist. Repository: {repo_key}")
            raise RepositoryNotFoundError(
                f"Not Found - The specified repository does not exist. Repository: {repo_key}")
        raise ArtifactoryError from error

    # Repositories operations
    def get(self, repo_key: str) -> ReplicationModel:
        """
        Find the repository and the replication configuration for it.

        :param repo_key: Name/key of the repository to retrieve
        :return: The configured replication model for the repository
        """
        try:
            response = self._get(route=f"{self._uri_with_s}/{repo_key}",
                                 headers={"accept": "application/json"},
                                 raise_for_status=True)
            response_data = response.json()
            logger.debug("Repository %s exists and loaded replication configuration", repo_key)
            return ReplicationModel.model_validate(response_data)

        except requests.exceptions.HTTPError as error:
            self._handle_exception(repo_key, error)


    def set(self, repo_key: str, replication: ReplicationModel) -> None:
        """
        Sets the replication configuration for a repository.
        :param repo_key: Name of the repository to set replication for
        :param replication: The replication model to set
        """
        try:
            self._put(route=f"{self._uri_with_s}/{repo_key}",
                      headers={"accept": "application/json", "Content-Type": "application/json"},
                      json=replication.model_dump(exclude_none=True, by_alias=True),
                      raise_for_status=True)

            logger.info(f"replication model set successfully for repository '{repo_key}'")

        except requests.exceptions.HTTPError as error:
            self._handle_exception(repo_key, error)


    def delete(self, repo_key: str) -> None:
        """
        deletes one or more replications for a repository.
        With multi-replication, all replications for the repository are deleted.
        """
        try:
            self._delete(route=f"{self._uri_with_s}/{repo_key}",
                         headers={"accept": "application/json"},
                         raise_for_status=True)

        except requests.exceptions.HTTPError as error:
            self._handle_exception(repo_key, error)

    def status(self, repo_key: str) -> ReplicationStatusModel:
        """ only for single replication, not for multi-replication - multi-replication needs Enterprise+ license. """
        try:
            response = self._get(route=f"{self._uri_without_s}/{repo_key}",
                                 headers={"accept": "application/json"},
                                 raise_for_status=True)

            response_data = response.json()
            return ReplicationStatusModel.model_validate(response_data)

        except requests.exceptions.HTTPError as error:
            self._handle_exception(repo_key, error)

    def update(self, repo_key: str, replication: ReplicationModel) -> None:
        """
        Updates the replication configuration for a repository.
        :param repo_key: Name of the repository to update
        :param replication: The replication model with updated values
        :return: The updated replication model
        """
        try:
            response = self._post(route=f"{self._uri_with_s}/{repo_key}",
                                  headers={"accept": "application/json", "Content-Type": "application/json"},
                                  json=replication.model_dump(exclude_none=True, by_alias=True),
                                  raise_for_status=True)

            # response_data = response.json()
            #
            # return ReplicationModel.model_validate(response_data)
            logger.info(f"replication model updated successfully: {response}")

        except requests.exceptions.HTTPError as error:
            self._handle_exception(repo_key, error)