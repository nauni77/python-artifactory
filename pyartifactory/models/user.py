"""
Definition of all user related models.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, SecretStr

from enum import Enum

class UserUpdateParamKeysEnum(str, Enum):
    """Enum of possible user parameters."""
    username = "username"
    email = "email"
    password = "password"
    admin = "admin"
    profile_updatable = "profile_updatable"
    internal_password_disabled = "internal_password_disabled"
    disable_ui_access = "disable_ui_access"

    # from Artifactory 7.128.0, the following fields are available
    watch_manager = "watch_manager"
    policy_viewer = "policy_viewer"
    policy_manager = "policy_manager"
    reports_manager = "reports_manager"
    resources_manager = "resources_manager"
    manage_webhooks = "manage_webhooks"
    platform_auditor = "platform_auditor"


class SimpleUser(BaseModel):
    """Models a simple user."""

    username: str
    uri: str | None = None
    status: str | None = None
    realm: str | None = None


class BaseUserModel(BaseModel):
    """
    Models a base user.
    https://www.jfrog.com/confluence/display/JFROG/Security+Configuration+JSON#SecurityConfigurationJSON-application/vnd.org.jfrog.artifactory.security.User+json
    """

    username: str
    admin: bool | None = None
    profile_updatable: bool | None = None
    disable_ui_access: bool | None = None
    internal_password_disabled: bool | None = None
    groups: List[str] | None = None

    # from Artifactory 7.128.0, the following fields are available
    watch_manager: bool | None = None
    policy_viewer: bool | None = None
    policy_manager: bool | None = None
    reports_manager: bool | None = None
    resources_manager: bool | None = None
    manage_webhooks: bool | None = None
    platform_auditor: bool | None = None


class User(BaseUserModel):
    """Models a user."""
    email: EmailStr | None = None


class NewUser(User):
    """Models a new user."""
    password: SecretStr

class UserResponse(User):
    """Models a user response."""
    status: str | None = None
    last_logged_in: datetime | None = None
    realm: str | None = None
