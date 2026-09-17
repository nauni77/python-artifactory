from __future__ import annotations

import json
import logging
from typing import List, overload

import requests

from pyartifactory.enums import ServiceType
from pyartifactory.exception import ArtifactoryError, RepositoryAlreadyExistsError, RepositoryNotFoundError
from pyartifactory.exception import handle_exception
from pyartifactory.models import AnyRepository, AnyRepositoryResponse
from pyartifactory.models.repository import (
    FederatedRepository,
    FederatedRepositoryResponse,
    LocalRepository,
    LocalRepositoryResponse,
    RClassEnum,
    RemoteRepository,
    RemoteRepositoryResponse,
    SimpleRepository,
    VirtualRepository,
    VirtualRepositoryResponse,
)
from pyartifactory.objects.object import ArtifactoryObject
from pyartifactory.utils import custom_encoder

logger = logging.getLogger("pyartifactory")


class ArtifactoryRepository(ArtifactoryObject):
    """
    Models an artifactory repository.
    API reference: https://docs.jfrog.com/artifactory/reference/createrepository
    """

    _uri = "repositories"

    # Repositories operations
    def get_repo(self, repo_name: str) -> AnyRepositoryResponse:
        """
        Finds repository in artifactory. Raises an exception if the repo doesn't exist.
        :param repo_name: Name of the repository to retrieve
        :return: Either a local, virtual, remote or federated repository
        """
        try:
            response = self._get(f"artifactory/api/{self._uri}/{repo_name}")
            response_data = response.json()

            try:
                r_class = response_data["rclass"]
            except KeyError:
                raise KeyError('"rclass" key not found in the response data received by artifactory.')

            # Match to the correct repository type depending on the r_class
            if r_class == RClassEnum.local:
                return LocalRepositoryResponse.model_validate(response_data)
            elif r_class == RClassEnum.virtual:
                return VirtualRepositoryResponse.model_validate(response_data)
            elif r_class == RClassEnum.remote:
                return RemoteRepositoryResponse.model_validate(response_data)
            elif r_class == RClassEnum.federated:
                return FederatedRepositoryResponse.model_validate(response_data)
            else:
                # this should never happen and is a missing repotype in the library
                raise ArtifactoryError(f"Unknown repository type found in response: {r_class}. Please report this issue.")
        except requests.exceptions.HTTPError as error:
            handle_exception(error, f"Repository {repo_name} does not exist", ServiceType.REPOSITORIES)

    @overload
    def create_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        ...

    @overload
    def create_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        ...

    @overload
    def create_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        ...

    @overload
    def create_repo(self, repo: FederatedRepository) -> FederatedRepositoryResponse:
        ...

    def create_repo(
        self,
        repo: AnyRepository,
    ) -> AnyRepositoryResponse:
        """
        Creates a local, virtual, remote or federated repository
        :param repo: Either a local, virtual, remote or federated repository
        :return: LocalRepositoryResponse, VirtualRepositoryResponse, RemoteRepositoryResponse
                 or FederatedRepositoryResponse object
        """
        repo_name = repo.key
        try:
            self.get_repo(repo_name)
        except RepositoryNotFoundError:
            ... # expected behavior, repository should not exist before creation
        else:
            logger.error("Repository %s already exists", repo_name)
            raise RepositoryAlreadyExistsError(f"Repository {repo_name} already exists")

        data = json.dumps(repo.model_dump(), default=custom_encoder)
        self._put(
            f"artifactory/api/{self._uri}/{repo_name}",
            headers={"Content-Type": "application/json"},
            data=data,
        )
        logger.debug("Repository %s successfully created", repo_name)
        return self.get_repo(repo_name)

    @overload
    def update_repo(self, repo: LocalRepository) -> LocalRepositoryResponse:
        ...

    @overload
    def update_repo(self, repo: VirtualRepository) -> VirtualRepositoryResponse:
        ...

    @overload
    def update_repo(self, repo: RemoteRepository) -> RemoteRepositoryResponse:
        ...

    @overload
    def update_repo(self, repo: FederatedRepository) -> FederatedRepositoryResponse:
        ...

    def update_repo(
        self,
        repo: AnyRepository,
    ) -> AnyRepositoryResponse:
        """
        Updates a local, virtual or remote repository
        :param repo: Either a local, virtual or remote repository
        :return: LocalRepositoryResponse, VirtualRepositoryResponse or RemoteRepositoryResponse object
        """
        repo_name = repo.key
        self.get_repo(repo_name)

        repo_dict = json.dumps(repo.model_dump(exclude_unset=True), default=custom_encoder)

        self._post(
            f"artifactory/api/{self._uri}/{repo_name}",
            headers={"Content-Type": "application/json"},
            data=repo_dict,
        )
        logger.debug("Repository %s successfully updated", repo_name)
        return self.get_repo(repo_name)

    # Remote repositories operations
    def list(self) -> List[SimpleRepository]:
        """
        Lists all the repositories
        :return: A list of repositories
        """
        response = self._get(f"artifactory/api/{self._uri}")
        logger.debug("List all repositories successful")
        return [SimpleRepository(**repository) for repository in response.json()]

    def delete(self, repo_name: str) -> None:
        """
        Removes a local repository
        :param repo_name: Name of the repository to delete
        :return: None
        """

        try:
            self._delete(f"artifactory/api/{self._uri}/{repo_name}")
        except requests.exceptions.HTTPError as error:
            handle_exception(error, f"repository {repo_name} delete fails", ServiceType.REPOSITORIES)
