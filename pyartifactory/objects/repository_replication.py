from __future__ import annotations

import logging

import requests

from pyartifactory.enums import ServiceType
from pyartifactory.exception import handle_exception
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
            handle_exception(error, "retrieve repository replication configuration failed", ServiceType.REPOSITORY_REPLICATION)


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
            handle_exception(error, "set repository replication configuration failed", ServiceType.REPOSITORY_REPLICATION)


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
            handle_exception(error, "delete repository replication configuration failed", ServiceType.REPOSITORY_REPLICATION)

    def status(self, repo_key: str) -> ReplicationStatusModel:
        """ only for single replication, not for multi-replication - multi-replication needs Enterprise+ license. """
        try:
            response = self._get(route=f"{self._uri_without_s}/{repo_key}",
                                 headers={"accept": "application/json"},
                                 raise_for_status=True)

            response_data = response.json()
            return ReplicationStatusModel.model_validate(response_data)

        except requests.exceptions.HTTPError as error:
            handle_exception(error, "retrieve repository replication status failed", ServiceType.REPOSITORY_REPLICATION)

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
            handle_exception(error, "update repository replication configuration failed", ServiceType.REPOSITORY_REPLICATION)