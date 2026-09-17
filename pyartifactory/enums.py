from enum import Enum


class ServiceType(Enum):
    """Enum for service types."""
    USERS = "users"
    GROUPS = "groups"
    SECURITY = "security"
    REPOSITORIES = "repositories"
    REPOSITORY_REPLICATION = "repository_replication"
    ARTIFACTS = "artifacts"
    PERMISSIONS = "permissions"
    BUILDS = "builds"
    SYSTEM = "system"
