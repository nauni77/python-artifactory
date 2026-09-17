"""
Definition of all exceptions.
"""

from __future__ import annotations

import logging
from typing import NoReturn, Union

import requests
from requests import Response

from pyartifactory.enums import ServiceType

logger = logging.getLogger("pyartifactory")


class ArtifactoryError(Exception):
    """Generic artifactory exception."""

class AlreadyExistsError(ArtifactoryError):
    """The requested object already exists."""


class UserAlreadyExistsError(AlreadyExistsError):
    """User already exists."""


class GroupAlreadyExistsError(AlreadyExistsError):
    """Group already exists."""


class RepositoryAlreadyExistsError(AlreadyExistsError):
    """Repository already exists."""


class PermissionAlreadyExistsError(AlreadyExistsError):
    """Permission already exists."""

class NotFoundError(ArtifactoryError):
    """The requested object was not found."""

class UserNotFoundError(NotFoundError):
    """The user was not found."""


class GroupNotFoundError(NotFoundError):
    """The group was not found."""


class RepositoryNotFoundError(NotFoundError):
    """The repository was not found."""


class PermissionNotFoundError(NotFoundError):
    """A permission object was not found."""


class ArtifactNotFoundError(NotFoundError):
    """An artifact was not found"""


class BadPropertiesError(ArtifactoryError):
    """Property value includes invalid characters"""


class PropertyNotFoundError(ArtifactoryError):
    """All requested properties were not found"""


class InvalidTokenDataError(ArtifactoryError):
    """The token contains invalid data."""


class BuildNotFoundError(NotFoundError):
    """Requested build were not found"""

class BadRequestError(ArtifactoryError):
    """The request body is malformed or a required parameter is missing."""

class BadCredentialsError(ArtifactoryError):
    """The credentials provided are invalid."""

class PermissionDeniedError(ArtifactoryError):
    """The user does not have permission to perform the requested operation."""


def handle_exception(error: requests.exceptions.HTTPError,
                     message: str,
                     service_type: ServiceType | None = None) -> NoReturn:
    """
    Handle HTTP errors and raise appropriate exceptions based on the status code and service type.
    :param error: The HTTPError exception raised by the request's library.
    :param service_type: The type of service (e.g., USERS, GROUPS, REPOSITORIES, etc.) that was being accessed when the error occurred.
    :param message: Additional information to include in the error message.
    :raises NotFoundError: If the resource was not found (HTTP 404).
    :raises BadCredentialsError: If the credentials provided are invalid (HTTP 401).
    :raises PermissionDeniedError: If the user does not have permission to perform the requested operation (HTTP 403).
    :raises ArtifactoryError: For other HTTP errors (e.g., 400, 409, 424, 500) or if the error does not match any specific case.
    """
    http_response: Union[Response, None] = error.response
    if isinstance(http_response, Response):
        if http_response.status_code == 400:
            if service_type == ServiceType.REPOSITORIES:
                logger.error(f"Bad Request - Repository not found or invalid key. Message: {message}")
                raise RepositoryNotFoundError(
                    f"Bad Request - Repository not found or invalid key. Message: {message}") from error
            elif service_type == ServiceType.USERS:
                logger.error(f"Bad Request - User not found or invalid key. Message: {message}")
                raise UserNotFoundError(
                    f"Bad Request - User not found or invalid key. Message: {message}") from error
            elif service_type == ServiceType.GROUPS:
                logger.error(f"Bad Request - Group not found or invalid key. Message: {message}")
                raise GroupNotFoundError(
                    f"Bad Request - Group not found or invalid key. Message: {message}") from error
            elif service_type == ServiceType.PERMISSIONS:
                logger.error(f"Bad Request - Permission not found or invalid key. Message: {message}")
                raise PermissionNotFoundError(
                    f"Bad Request - Permission not found or invalid key. Message: {message}") from error
            elif service_type == ServiceType.ARTIFACTS:
                logger.error(f"Bad Request - Artifact not found or invalid key. Message: {message}")
                raise ArtifactNotFoundError(
                    f"Bad Request - Artifact not found or invalid key. Message: {message}") from error
            elif service_type == ServiceType.SYSTEM:
                logger.error("Artifactory license key installation failed: invalid license key.")
                raise BadRequestError("Artifactory license key installation failed: invalid license key.") from error
            else:
                logger.error(f"Bad Request - not found or invalid key. Message: {message}")
                raise NotFoundError(f"Bad Request - not found or invalid key. Message: {message}") from error

        elif http_response.status_code == 401:
            logger.error(f"Bad Credentials - Authentication failed. A valid token is required. Message: {message}")
            raise BadCredentialsError(
                f"Bad Credentials - Authentication failed. A valid token is required. Message: {message}") from error
        elif http_response.status_code == 403:
            logger.error(f"Permission Denied - User does not have admin permissions. Message: {message}")
            raise PermissionDeniedError(
                f"Permission Denied - User does not have admin permissions. Message: {message}") from error
        elif http_response.status_code == 404:
            if service_type == ServiceType.REPOSITORIES:
                logger.error(f"Not Found - The specified repository does not exist or invalid key. Message: {message}")
                raise RepositoryNotFoundError(
                    f"Not Found - The specified repository does not exist or invalid key. Message: {message}") from error
            elif service_type == ServiceType.USERS:
                logger.error(f"Not Found - The specified user does not exist or invalid key. Message: {message}")
                raise UserNotFoundError(
                    f"Not Found - The specified user does not exist or invalid key. Message: {message}") from error
            elif service_type == ServiceType.GROUPS:
                logger.error(f"Not Found - The specified group does not exist or invalid key. Message: {message}")
                raise GroupNotFoundError(
                    f"Not Found - The specified group does not exist or invalid key. Message: {message}") from error
            elif service_type == ServiceType.PERMISSIONS:
                logger.error(f"Not Found - The specified permission does not exist or invalid key. Message: {message}")
                raise PermissionNotFoundError(
                    f"Not Found - The specified permission does not exist or invalid key. Message: {message}") from error
            elif service_type == ServiceType.ARTIFACTS:
                logger.error(f"Not Found - The specified artifact does not exist or invalid key. Message: {message}")
                raise ArtifactNotFoundError(
                    f"Not Found - The specified artifact does not exist or invalid key. Message: {message}") from error
            else:
                logger.error(f"Not Found - The specified repository does not exist or invalid key. Message: {message}")
                raise NotFoundError(
                    f"Not Found - The specified repository does not exist or invalid key. Message: {message}") from error
        elif http_response.status_code == 409:
            logger.error(f"Conflict - Import still in progress, or a worker vetoed deletion. Message: {message}")
            raise ArtifactoryError(
                f"Conflict - Import still in progress, or a worker vetoed deletion. Message: {message}") from error
        elif http_response.status_code == 424:
            logger.error(f"Failed Dependency - The repository is a member of a federated repository. Message: {message}")
            raise ArtifactoryError(
                f"Failed Dependency - The repository is a member of a federated repository. Message: {message}") from error
        elif http_response.status_code == 500:
            logger.error(f"Internal Server Error - unexpected failure or lock acquisition failure. Message: {message}")
            raise ArtifactoryError(
                f"Internal Server Error - unexpected failure or lock acquisition failure. Message: {message}") from error

    raise ArtifactoryError() from error