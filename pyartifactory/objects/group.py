from __future__ import annotations

import logging
from typing import List, Union

import requests
from requests import Response

from pyartifactory.exception import ArtifactoryError, GroupAlreadyExistsError, GroupNotFoundError
from pyartifactory.models.group import SimpleGroup, GroupDetails, NewGroup, GroupUpdateParamKeysEnum
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactoryGroup(ArtifactoryObject):
    """
    Manipulate artifactory groups
    API documentation: https://docs.jfrog.com/administration/reference/creategroup

    This is also moved from `/artifactory/` to `/access/` and needs to be updated!
    """

    _uri_v2 = "access/api/v2/groups"

    def create(self, group: NewGroup) -> GroupDetails:
        """
        Creates a new group in Artifactory or replaces an existing group
        :param group: the group to create
        :return: Created group
        """
        group_name = group.name
        try:
            self.get(group_name)
            logger.error("Group %s already exists", group_name)
            raise GroupAlreadyExistsError(f"Group {group_name} already exists")
        except GroupNotFoundError:
            response: Response = self._post(f"{self._uri_v2}",
                       headers={"accept": "application/json", "content-type": "application/json"},
                       json=group.model_dump(exclude_none=True))
            result_group: GroupDetails = GroupDetails(**response.json())
            logger.debug("Group %s successfully created", result_group.name)
            return result_group


    def get(self, group_name: str) -> GroupDetails:
        """
        get the details of an Artifactory group
        API reference: https://docs.jfrog.com/administration/reference/getgroupdetails

        :param group_name: name of the group to retrieve
        :return: artifactory group
        """
        try:
            response = self._get(f"{self._uri_v2}/{group_name}", headers={"accept": "application/json"})
            logger.debug("Group %s found", group_name)
            return GroupDetails(**response.json())
        except requests.exceptions.HTTPError as error:
            http_response: Union[Response, None] = error.response
            if isinstance(http_response, Response) and http_response.status_code in (404, 400):
                logger.error("Group %s does not exist", group_name)
                raise GroupNotFoundError(f"Group {group_name} does not exist")
            raise ArtifactoryError from error


    def list(self) -> List[SimpleGroup]:
        """
        lists all the groups
        API reference: https://docs.jfrog.com/administration/reference/getgrouplist

        :return: list of all groups in Artifactory
        """
        response = self._get(f"{self._uri_v2}")
        logger.debug("List all groups successful")
        return [SimpleGroup(**group) for group in response.json().get("groups", [])]


    def update_partial(self, group_name: str,
               data: dict[GroupUpdateParamKeysEnum, object]) -> GroupDetails:
        """
        updates an exiting group in Artifactory with the provided group details
        API reference: https://docs.jfrog.com/administration/reference/updategroup

        :param group_name: group name to be modified
        :param data: dictionary of group details to be updated,
                       if provided, it will be used to update the group - details_values will be ignored
        :return: details of the updated group
        """
        # check if group exists, if not, raise an exception
        self.get(group_name)

        response: Response = self._patch(f"{self._uri_v2}/{group_name}",
                                         headers={"accept": "application/json", "content-type": "application/json"},
                                         json=data)
        result: GroupDetails = GroupDetails(**response.json())
        logger.debug(f"Group {group_name} successfully updated")
        return result

    def update(self, group_name: str,
               data: GroupDetails) -> GroupDetails:
        """
        updates an exiting group in Artifactory with the provided group details
        API reference: https://docs.jfrog.com/administration/reference/updategroup

        :param group_name: group name to be modified
        :param values: dictionary of group details to be updated,
                       if provided, it will be used to update the group - details_values will be ignored
        :param data: optional GroupDetails object to be updated
        :return: details of the updated group
        """
        values = data.model_dump(exclude_none=True) if data is not None else {}
        return self.update_partial(group_name, values)

    def delete(self, group_name: str) -> None:
        """
        removes a group
        API reference: https://docs.jfrog.com/administration/reference/deletegroup

        :param group_name: name of the group to delete
        :return: None
        """
        # check if group exists, if not, raise an exception
        self.get(group_name)
        self._delete(f"{self._uri_v2}/{group_name}")
        logger.debug(f"Group {group_name} successfully deleted")


    def modify_group_members(self, group_name: str, add: list[str], remove: list[str]) -> GroupDetails:
        """
        Adds or removes members from a group.
        API reference: https://docs.jfrog.com/administration/reference/updategroupmembers

        :param group_name: name of the group to modify
        :param add: list of usernames to add to the group
        :param remove: list of usernames to remove from the group
        :return: details of the updated group
        """
        # check if group exists, if not, raise an exception
        self.get(group_name)

        payload = {"add": add, "remove": remove}
        response: Response = self._patch(f"{self._uri_v2}/{group_name}/members",
                    headers={"accept": "application/json", "content-type": "application/json"},
                    json=payload)

        # response contains only the 'members' of this group, not the complete group details
        result: GroupDetails = self.get(group_name)
        logger.debug(f"Group {group_name} members successfully modified")
        return result
