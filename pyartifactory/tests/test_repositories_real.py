from __future__ import annotations

import unittest

from pyartifactory.models import SimpleRepository, LocalRepository, LocalRepositoryResponse
from pyartifactory.tests.base_test_real import TestBaseReal
from pyartifactory.tests.data.data import TestData

from pyartifactory.models.repository import PackageTypeEnum
from pyartifactory.exception import RepositoryNotFoundError

class TestRepositoriesReal(TestBaseReal):
    """
    check to get, create, delete, ... repositories in artifactory by using API.
    API reference: https://docs.jfrog.com/artifactory/reference/createrepository
    """

    def setUp(self) -> None:
        super().setUp()
        self.logger.info("setting up the test class for TestRepositoriesReal")
        self._client = TestRepositoriesReal.CLIENT_TARGET

    def cleanup_repository(self, repository_name: str) -> bool:
        # check if repository already exists and delete it if it does
        try:
            self._client.repositories.get_repo(repository_name)
            self.logger.info(f"Repository '{repository_name}' already exists, deleting it for testing...")
            self._client.repositories.delete(repository_name)
            self.logger.info(f"Repository '{repository_name}' deleted")
            return True
        except RepositoryNotFoundError:
            self.logger.info(f"Repository '{repository_name}' does not exist, continue without deleting it")
        return False

    def test_get_repositories_list_and_detail(self) -> None:
        """
        This works on new artifactory and at the old API
        """
        result: list[SimpleRepository] = self._client.repositories.list()
        self.assertGreater(len(result), 0, "no repositories found in Artifactory")

    def test_get_delete_create_repository(self) -> None:
        """
        This works on new artifactory and at the old API
        """
        self.assertEqual(TestData.TEST_REPOSITORIES_LOCAL[0].package_type, PackageTypeEnum.generic,
                         "test repository package type of the first entry is not generic, as expected")
        test_repo_generic_name = TestData.TEST_REPOSITORIES_LOCAL[0].name
        test_repo_generic_description = TestData.TEST_REPOSITORIES_LOCAL[0].description

        self.cleanup_repository(test_repo_generic_name)

        # create a new repository
        new_repository: LocalRepository = LocalRepository(
            key=test_repo_generic_name,
            description=test_repo_generic_description,
            packageType=PackageTypeEnum.generic,
        )
        created_repo: LocalRepositoryResponse = self._client.repositories.create_repo(new_repository)
        self.logger.info(f"Repository '{created_repo.key}' created")
        self.assertEqual(created_repo.key, test_repo_generic_name, "created repository name does not match")
        self._client.repositories.delete(test_repo_generic_name)
        self.logger.info(f"Repository '{test_repo_generic_name}' deleted, cleanup completed")


    def test_update_repository(self) -> None:
        """
        This works on new artifactory and at the old API
        """
        self.assertEqual(TestData.TEST_REPOSITORIES_LOCAL[0].package_type, PackageTypeEnum.generic,
                         "test repository package type of the first entry is not generic, as expected")
        test_repo_generic_name = TestData.TEST_REPOSITORIES_LOCAL[0].name
        test_repo_generic_description = TestData.TEST_REPOSITORIES_LOCAL[0].description

        self.cleanup_repository(test_repo_generic_name)

        # create a new repository
        new_repository: LocalRepository = LocalRepository(
            key=test_repo_generic_name,
            description=test_repo_generic_description,
            packageType=PackageTypeEnum.generic,
        )
        created_repo: LocalRepositoryResponse = self._client.repositories.create_repo(new_repository)
        self.logger.info(f"Repository '{created_repo.key}' created")

        new_description = "some other description for testing repository"
        self.assertNotEqual(new_description, created_repo.description, "new description was changed and should be different from the original")
        created_repo.description = new_description
        updated_repo: LocalRepositoryResponse = self._client.repositories.update_repo(created_repo)
        self.assertEqual(updated_repo.description, new_description, "updated repository description does not match")

        new_description_2 = "some other description for testing repository_2"
        test_generic_repo: LocalRepositoryResponse = self._client.repositories.get_repo(test_repo_generic_name)
        test_generic_repo.description = new_description_2
        updated_repo_2: LocalRepositoryResponse = self._client.repositories.update_repo(test_generic_repo)
        self.assertEqual(updated_repo_2.description, new_description_2, "updated repository description does not match")

        self.logger.info(f"Tests repository update completed successfully, start cleanup")
        self.cleanup_repository(test_repo_generic_name)
        self.logger.info(f"Test repository '{test_repo_generic_name}' update, cleanup completed")

if __name__ == '__main__':
  unittest.main()