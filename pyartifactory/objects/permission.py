from __future__ import annotations

import logging
from typing import List, Union, overload

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, PermissionAlreadyExistsError, PermissionNotFoundError
from pyartifactory.models import AnyPermission
from pyartifactory.models.auth import AuthModel
from pyartifactory.models.permission import Permission, PermissionV2, SimplePermission
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryPermission(ArtifactoryObject):
    """
    Models an artifactory permission.

    There is an API to manage permissions for repositories only:
    (since 2.4.0 - v1, still present at API)
    https://docs.jfrog.com/administration/reference/getpermissiontargets
    (since 6.6.0 - v2, manage repositories, builds and release bundles)
    https://docs.jfrog.com/administration/reference/getpermissiontargetsv2

    Additionally, there is another API to manage permissions for repositories, builds and release bundles:
    (7.72.0+; expands in 7.210.0+)
    https://docs.jfrog.com/administration/reference/getpermissions
    Laut Doku ersetzt dieser Endpunkt die alten Abfragen
      GET /artifactory/api/v2/security/permissions/users/{user}
    bzw.
      GET /artifactory/api/v2/security/permissions/groups/{group}
    . Zudem:
      - Paginierung (curser, limit)
      - Filter by user/group
      - include inherited groups (a user will be found by his group memberships)
      - direct expand details for user/group (expand=true)
      - Scoped Token (system:permissions:r) - read without admin rights

    => We don't need currently the new API.
    => We want to start with artifactory 7.77.7, so we need to use the first API.
    """

    def __init__(self, artifactory: AuthModel) -> None:
        super().__init__(artifactory)
        if self._api_version == 2:
            # https://docs.jfrog.com/administration/reference/getpermissiontargetsv2
            self._uri = "v2/security/permissions"
        elif self._api_version == 1:
            # https://docs.jfrog.com/administration/reference/getpermissiontargets
            self._uri = "security/permissions"
        else:
            raise ArtifactoryError(f"Unsupported API version: {self._api_version}")

    @overload
    def create(
        self,
        permission: Permission,
    ) -> Permission:
        ...

    @overload
    def create(
        self,
        permission: PermissionV2,
    ) -> PermissionV2:
        ...

    def create(self, permission: AnyPermission) -> AnyPermission:
        """
        Creates, replace/update a permission
        API v2: https://docs.jfrog.com/administration/reference/createorreplacepermissiontargetv2

        :param permission:  v2 or v1 object
        :return: Permission v2 or v1
        """
        permission_name = permission.name
        try:
            self.get(permission_name)
            logger.debug("Permission %s already exists", permission_name)
            raise PermissionAlreadyExistsError(f"Permission {permission_name} already exists")
        except PermissionNotFoundError:
            # v2 URL (create, replace, update)
            # PUT: https://{jfrog_url}/artifactory/api/v2/security/permissions/{permissionTargetName}

            # define application/json for the request
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
            }

            # payload: str = permission.model_dump_json(by_alias=True, exclude={"name"}, exclude_none=True)
            # payload: str = permission.model_dump_json(by_alias=True, exclude_none=True)

            ## THIS IS WORKING!!!
            # payload = {"repo": {
            #     "repositories": ["py_test-pypi", "py_test-maven", "py_test-docker"],
            #     "actions": {
            #         "users": {"py_test": ["read", "write"]},
            #         "groups": {"py_test": ["read"]}
            #     }
            # }}

            self._put(
                f"artifactory/api/{self._uri}/{permission_name}",
                json=permission.model_dump(by_alias=True, exclude_none=True),
                headers=headers,
            )
            logger.debug("Permission %s successfully created", permission_name)
            return self.get(permission_name)

    def get(self, permission_name: str) -> AnyPermission:
        """
        Get detailed permission from artifactory.
        API: https://docs.jfrog.com/administration/reference/getpermissiondetails

        :param permission_name: Name of the permission to retrieve
        :return: AnyPermission object (Permission v2 or v1)
        """
        try:
            # v2 URL (get)
            # GET: https://{jfrog_url}/artifactory/api/v2/security/permissions/{permissionTargetName}
            response = self._get(f"artifactory/api/{self._uri}/{permission_name}")
            logger.debug("Permission %s found", permission_name)
            return (
                Permission(**response.json()) if self._artifactory.api_version == 1 else PermissionV2(**response.json())
            )
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("Permission %s does not exist", permission_name)
                raise PermissionNotFoundError(f"Permission {permission_name} does not exist")
            raise ArtifactoryError from error

    def list(self) -> List[SimplePermission]:
        """
        Lists all the permissions
        API: https://docs.jfrog.com/administration/reference/getpermissions

        :return: A list of permissions
        """
        # TODO: new API
        #       GET: https://{jfrog_url}/access/api/v2/permissions
        response = self._get(f"artifactory/api/{self._uri}")
        logger.debug("List all permissions successful")
        return [SimplePermission(**permission) for permission in response.json()]

    @overload
    def update(self, permission: Permission) -> Permission:
        ...

    @overload
    def update(self, permission: PermissionV2) -> PermissionV2:
        ...

    def update(self, permission: AnyPermission) -> AnyPermission:
        """
        Updates an artifactory permission. I don't know the exact difference between the two APIs,
        but I think it's like this:
        API: PUT: https://docs.jfrog.com/administration/reference/replacepermissionresource
        => replaces the entire permission resource with the new one, and if you don't include a field,
           it will be removed from the permission.
        and
        API: PATCH: https://docs.jfrog.com/administration/reference/updatepermissionresource
        => updates the permission resource with the new one, and if you don't include a field,
           it will be left unchanged. I think this will only extend an existing permission,
           but not remove any existing fields.

        Because of this I will implement the PUT method to also delete parts of the permissions!
        The handling is to load the permission and then update it with the new permission,
        and then send the entire permission back to the server. So the whole permission should fit the new description.

        :param permission: AnyPermission v2 or v1 object
        :return: AnyPermission v2 or v1 object
        """
        permission_name = permission.name
        self._put(
            f"artifactory/api/{self._uri}/{permission_name}",
            json=permission.model_dump(by_alias=True),
        )
        logger.debug("Permission %s successfully updated", permission_name)
        return self.get(permission_name)

    def delete(self, permission_name: str) -> None:
        """
        Removes an artifactory permission
        API: https://docs.jfrog.com/administration/reference/deletepermission

        :param permission_name: Name of the permission to delete
        :return: None
        """
        self.get(permission_name)
        # TODO: new API
        #       https://{jfrog_url}/access/api/v2/permissions/{permissionName}
        self._delete(f"artifactory/api/{self._uri}/{permission_name}")
        logger.debug("Permission %s successfully deleted", permission_name)
