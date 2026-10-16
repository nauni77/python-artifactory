from dataclasses import dataclass, field
import logging
from sys import prefix

from pydantic import SecretStr

from pyartifactory import Artifactory
from pyartifactory.exception import UserNotFoundError, GroupNotFoundError, RepositoryNotFoundError, \
    PermissionNotFoundError
from pyartifactory.models import NewUser, NewGroup, PermissionV2
from pyartifactory.models.permission import PermissionEnumV2, RepoV2, PrincipalsPermissionV2
from pyartifactory.models.repository import PackageTypeEnum, LocalRepository


@dataclass
class TestAuthConfig:
    """
    This class is used to store the test configuration for the real tests.
    """
    # URL to the artifactory instance (example: https://my-repo.my-domain.de).
    url: str
    # Bearer token form Artifactory for authentication (example: "eyJhbGciOiJIUzI1NiI...J9").
    bearer_token: str | None
    # username for authentication (example: "admin"), only used if no bearer token is provided.
    username: str | None
    # password for authentication (example: "my-password"), only used if no bearer token is provided.
    password: str | None
    # Tuple of username and password for authentication (example: ("admin", SecretStr("my-password"))).
    # Just used if no bearer token is provided.
    auth: tuple[str, SecretStr] | None = field(init=False, default=None)

    def __post_init__(self):
        self.auth = (
            (self.username, SecretStr(self.password))
            if self.username is not None and self.password is not None
            else None
        )


@dataclass
class TestUser:
    prefix: str
    username: str
    password: str
    email: str

    def __post_init__(self):
        if not self.username.startswith(f"{self.prefix}"):
            raise ValueError("username need to start with prefix, no suffix is needed")

@dataclass
class TestGroup:
    prefix: str
    name: str
    description: str
    auto_join: bool = False
    external_id: str | None = None
    members: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.name.startswith(f"{self.prefix}"):
            raise ValueError("group name need to start with prefix, no suffix is needed")

@dataclass
class TestRepositoryLocal:
    prefix: str
    name: str
    description: str
    package_type: PackageTypeEnum

    def __post_init__(self):
        if not self.name.startswith(f"{self.prefix}-"):
            raise ValueError("name need to start with prefix- followed by a non-empty string")

@dataclass
class TestRepositoryRemote:
    prefix: str
    name: str
    description: str
    url: str
    package_type: PackageTypeEnum

    def __post_init__(self):
        if not self.name.startswith(f"{self.prefix}-"):
            raise ValueError("name need to start with prefix- followed by a non-empty string")

@dataclass
class TestRepositoryVirtual:
    prefix: str
    name: str
    package_type: PackageTypeEnum
    repositories: list[str]  # List of repository names included in the virtual repository

    def __post_init__(self):
        if not self.name.startswith(f"{self.prefix}-"):
            raise ValueError("name need to start with prefix- followed by a non-empty string")

@dataclass
class TestPermission:
    prefix: str
    name: str
    repositories: list[str]
    principals_user: dict[str, list[PermissionEnumV2]]
    principals_group: dict[str, list[PermissionEnumV2]]

    def __post_init__(self):
        if not self.name.startswith(f"{self.prefix}-"):
            raise ValueError("name need to start with prefix- followed by a non-empty string")


class TestData:
    """
    This class contains test data for the tests and additional methods for easier handling:
    - create and clean test users
    - create and clean test groups
    - create and clean test repositories
    - create and clean test permissions
    - cleanup all test data
    """

    TEST_USERS: list[TestUser] = [
        TestUser(prefix="py_test",
                 username="py_test",
                 password="pyTest123user+pwd",
                 email="test.user@noventi.de"),
    ]

    TEST_GROUPS: list[TestGroup] = [
        TestGroup(prefix="py_test",
                  name="py_test",
                  description="This is a test group created by TestGroupsReal",
                  auto_join=False,
                  external_id="maybe_later_to_use_with_ldap",
                  members=["py_test"]),
    ]

    TEST_REPOSITORIES_LOCAL: list[TestRepositoryLocal] = [
        TestRepositoryLocal(
            prefix="py_test",
            name="py_test-generic",
            description="py_test_generic repository for testing",
            package_type=PackageTypeEnum.generic
        ),
        TestRepositoryLocal(
            prefix="py_test",
            name="py_test-maven",
            description="py_test_maven repository for testing",
            package_type=PackageTypeEnum.maven
        ),
        TestRepositoryLocal(
            prefix="py_test",
            name="py_test-pypi",
            description="py_test_pypi repository for testing",
            package_type=PackageTypeEnum.pypi
        ),
        TestRepositoryLocal(
            prefix="py_test",
            name="py_test-docker",
            description="py_test_docker repository for testing",
            package_type=PackageTypeEnum.docker
        ),
        # "npm": "py_test-npm",
        # "ivy": "py_test-ivy",
        # "nuget": "py_test-nuget",
    ]

    TEST_REPOSITORIES_REMOTE: list[TestRepositoryRemote] = [
        TestRepositoryRemote(
            prefix="py_test",
            name="py_test-remote-maven",
            description="py_test-remote-maven repository for testing",
            package_type=PackageTypeEnum.maven,
            url="https://repo1.maven.org/maven2/",
        ),
        TestRepositoryRemote(
            prefix="py_test",
            name="py_test-remote-docker",
            description="py_test-remote-docker repository for testing",
            package_type=PackageTypeEnum.docker,
            url="https://registry-1.docker.io/",
        ),
    ]

    TEST_REPOSITORIES_VIRTUAL: list[TestRepositoryVirtual] = [
        TestRepositoryVirtual(
            prefix="py_test",
            name="py_test-maven-virtual",
            package_type=PackageTypeEnum.maven,
            repositories=["py_test-remote-maven", "py_test-maven"]
        ),
        TestRepositoryVirtual(
            prefix="py_test",
            name="py_test-docker-virtual",
            package_type=PackageTypeEnum.docker,
            repositories=["py_test-remote-docker", "py_test-docker"]
        ),
    ]

    TEST_PERMISSIONS: list[TestPermission] = [
        TestPermission(
            prefix="py_test",
            name="py_test-01",
            repositories=["py_test-pypi", "py_test-maven", "py_test-docker"],
            principals_user={"py_test": [PermissionEnumV2.read, PermissionEnumV2.write]},
            principals_group={"py_test": [PermissionEnumV2.read]}
        ),
    ]

    @staticmethod
    def create_permissions(client: Artifactory):
        """
        Creates the defined test permissions at the Artifactory instance the client refers to.
        """
        for cur_permission in TestData.TEST_PERMISSIONS:
            try:
                client.permissions.get(cur_permission.name)
                logging.getLogger("TestData").info(f"test permission already exists ({cur_permission.name})")
            except PermissionNotFoundError:
                logging.getLogger("TestData").info(f"test permission not exists, create the permission ({cur_permission.name})")
                actions: PrincipalsPermissionV2 = PrincipalsPermissionV2(
                    users=cur_permission.principals_user,
                    groups=cur_permission.principals_group
                )
                repos: RepoV2 = RepoV2(repositories=cur_permission.repositories, actions=actions)
                permission: PermissionV2 = PermissionV2(name=cur_permission.name, repo=repos)
                client.permissions.create(permission)

    @staticmethod
    def cleanup_permissions(client: Artifactory):
        """
        This method cleans the test permissions from Artifactory instance the client refers to.
        @param: client The client to the artifactory to execute the changes.
        """
        for cur_permission in TestData.TEST_PERMISSIONS:
            try:
                client.permissions.delete(cur_permission.name)
                logging.getLogger("TestData").info(f"test permission deleted ({cur_permission.name})")
            except PermissionNotFoundError:
                logging.getLogger("TestData").info(f"test permission not found, nothing to delete ({cur_permission.name})")

    @staticmethod
    def create_users(client: Artifactory):
        """
        Creates the defined test users at the Artifactory instance the client refers to.
        """
        for cur_user in TestData.TEST_USERS:
            try:
                client.users.get(cur_user.username)
                logging.getLogger("TestData").info(f"test user already exists ({cur_user.username})")
            except UserNotFoundError:
                logging.getLogger("TestData").info(f"test user not exists, create the user ({cur_user.username})")
                client.users.create(NewUser(
                    username=cur_user.username,
                    email=cur_user.email,
                    password=SecretStr(cur_user.password),
                    admin=False,
                    profile_updatable=True))

    @staticmethod
    def cleanup_users(client: Artifactory):
        """
        This method cleans the test users from Artifactory instance the client refers to.
        @param: client The client to the artifactory to execute the changes.
        """
        for cur_user in TestData.TEST_USERS:
            try:
                client.users.delete(cur_user.username)
                logging.getLogger("TestData").info(f"test user deleted ({cur_user.username})")
            except UserNotFoundError:
                logging.getLogger("TestData").info(f"test user not found, nothing to delete ({cur_user.username})")

    @staticmethod
    def create_groups(client: Artifactory):
        """
        Creates the defined test groups at the Artifactory instance the client refers to.
        """
        for cur_group in TestData.TEST_GROUPS:
            try:
                client.groups.get(cur_group.name)
                logging.getLogger("TestData").info(f"test group already exists ({cur_group.name})")
            except GroupNotFoundError:
                logging.getLogger("TestData").info(f"test group not exists, create the group ({cur_group.name})")
                client.groups.create(NewGroup(
                    name=cur_group.name,
                    description=cur_group.description,
                    members=cur_group.members))

    @staticmethod
    def cleanup_groups(client: Artifactory):
        """
        This method cleans the test groups from Artifactory instance the client refers to.
        @param: client The client to the artifactory to execute the changes.
        """
        for cur_group in TestData.TEST_GROUPS:
            try:
                client.groups.delete(cur_group.name)
                logging.getLogger("TestData").info(f"test group deleted ({cur_group.name})")
            except GroupNotFoundError:
                logging.getLogger("TestData").info(f"test group not found, nothing to delete ({cur_group.name})")

    @staticmethod
    def create_repositories(client: Artifactory):
        """
        Creates the defined test repositories at the Artifactory instance the client refers to.
        """
        for cur_repo in TestData.TEST_REPOSITORIES_LOCAL:
            try:
                client.repositories.get_repo(cur_repo.name)
                logging.getLogger("TestData").info(f"test repository already exists ({cur_repo.name})")
            except RepositoryNotFoundError:
                logging.getLogger("TestData").info(f"test repository not exists, create the repository ({cur_repo.name})")
                client.repositories.create_repo(LocalRepository(
                    key=cur_repo.name,
                    packageType=cur_repo.package_type,
                    description=cur_repo.description))

    @staticmethod
    def cleanup_repositories(client: Artifactory):
        """
        This method cleans the test repositories from Artifactory instance the client refers to.
        @param: client The client to the artifactory to execute the changes.
        """
        for cur_repo in TestData.TEST_REPOSITORIES_LOCAL:
            try:
                client.repositories.delete(cur_repo.name)
                logging.getLogger("TestData").info(f"test repository deleted ({cur_repo.name})")
            except RepositoryNotFoundError:
                logging.getLogger("TestData").info(f"test repository not found, nothing to delete ({cur_repo.name})")

    @staticmethod
    def cleanup(client: Artifactory):
        """
        At the Artifactory the client is logged in,
        this method removes all created test data, which is defined in this class.
        @param: client The client to the artifactory to execute the changes.
        """
        TestData.cleanup_permissions(client)
        TestData.cleanup_groups(client)
        TestData.cleanup_users(client)
        TestData.cleanup_repositories(client)