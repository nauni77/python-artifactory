"""
Definition of all group models.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

class GroupUpdateParamKeysEnum(str, Enum):
    """ Enum of possible group parameters """
    name = "username"
    description = "description"
    auto_join = "auto_join"
    admin_privileges = "admin_privileges"
    external_id = "external_id"

    # from Artifactory 7.128.0, the following fields are available
    reports_manager = "reports_manager"
    watch_manager = "watch_manager"
    policy_manager = "policy_manager"

    policy_viewer = "policy_viewer"
    manage_resources = "manage_resources"
    manage_webhook = "manage_webhook"


class SimpleGroup(BaseModel):
    """ Models a simple group, which is returned by the list of groups and contains only real basic information. """
    group_name: str
    uri: str | None = None


class GroupBase(BaseModel):
    name: str
    description: str | None = None
    auto_join: bool | None = None
    admin_privileges: bool | None = None

    members: List[str] | None = None        # only available in CREATE and GET - NOT UPDATE!

class GroupDetails(GroupBase):
    """ Models a group, which is returned by getting details of a group and contains all information. """
    realm: str | None = None                # only available in GET, not in CREATE or UPDATE
    realm_attributes: str | None = None     # only available in GET, not in CREATE or UPDATE
    external_id: str | None = None          # not available in GET

    # since Artifactory 7.128.0, the following fields are available
    reports_manager: bool | None = None
    watch_manager: bool | None = None
    policy_manager: bool | None = None
    policy_viewer: bool | None = None
    manage_resources: bool | None = None
    manage_webhook: bool | None = None      # not in GET

class NewGroup(GroupDetails):
    """Models a new group"""
    pass
