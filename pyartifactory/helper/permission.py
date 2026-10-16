import logging
from pyartifactory import Artifactory
from pyartifactory.models import PermissionV2, SimpleUser


def clean_users(client: Artifactory, permission: PermissionV2) -> None:
    """
    Clean up all users in the Artifactory instance.
    """
    all_users = client.users.list()
    all_users_dict: dict[str, SimpleUser] = {user.username: user for user in all_users}

    if permission.repo is None:
        logging.debug(f"Permission '{permission.name}' has no repository defined, skipping user cleanup.")
        return

    if permission.repo.actions.users is None:
        logging.debug(f"Permission '{permission.name}' has no users defined, skipping user cleanup.")
        return

    for cur in set(permission.repo.actions.users.keys()):
        if cur not in all_users_dict:
            permission.repo.actions.users.pop(cur)
            logging.warning(f"User '{cur}' not found in Artifactory, removed from permission '{permission.name}'")

def clean_groups(client: Artifactory, permission: PermissionV2) -> None:
    """
    Clean up all groups in the Artifactory instance.
    """
    all_groups = client.groups.list()
    all_groups_dict: dict[str, str] = {group.group_name: group.group_name for group in all_groups}

    if permission.repo is None:
        logging.debug(f"Permission '{permission.name}' has no repository defined, skipping group cleanup.")
        return

    if permission.repo.actions.groups is None:
        logging.debug(f"Permission '{permission.name}' has no groups defined, skipping group cleanup.")
        return

    for cur in set(permission.repo.actions.groups.keys()):
        if cur not in all_groups_dict:
            permission.repo.actions.groups.pop(cur)
            logging.warning(f"Group '{cur}' not found in Artifactory, removed from permission '{permission.name}'")


def clean_permission(client: Artifactory, permission: PermissionV2) -> None:
    """
    clean user and groups in the permission object by removing any users or groups that do not exist in the Artifactory instance.
    TODO: maybe also remote not existing repositories from target ...
    """
    clean_users(client, permission)
    clean_groups(client, permission)