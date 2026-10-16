from __future__ import annotations

import os
import unittest

from pydantic import SecretStr

from pyartifactory.exception import RepositoryNotFoundError
from pyartifactory.models import SimpleRepository, RemoteRepositoryResponse
from pyartifactory.models.repository import RClassEnum, PackageTypeEnum
from pyartifactory.models.repository_replication import ReplicationModel, ReplicationStatusModel, ReplicationStatusEnum
from pyartifactory.tests.base_test_real import TestBaseReal


class TestRepositoriesReplicationReal(TestBaseReal):
    """
    This class check to add/remove/update replications to repositories in artifactory by using API.
    API reference: https://docs.jfrog.com/artifactory/reference/getrepositoryreplicationconfiguration

    TODO: this test is not general possible only with my test data - because of this it needs to be overworked
    """

    def setUp(self) -> None:
        super().setUp()
        self.logger.info("setting up the test class for TestRepositoriesReplicationReal")
        # only 01 has replications added
        self._client = TestRepositoriesReplicationReal.CLIENT_SOURCE
        self.test_repo_key: str = "test-pypi"

    def test_00_load_repository_replication(self) -> None:
        """
        Load a repository replication
        """
        try:
            self._client.repository_replication.get("test_unknown_repo")
        except RepositoryNotFoundError as e:
            self.logger.info(f"RepositoryNotFoundError thrown as expected - repo does not exist!")

        repl_model: ReplicationModel = self._client.repository_replication.get(self.test_repo_key)
        self.logger.info(f"replication model loaded: {repl_model}")

    def test_01_load_repository_replication_status(self) -> None:
        """ Load a repository replication status """
        status: ReplicationStatusModel = self._client.repository_replication.status(self.test_repo_key)
        self.logger.info(f"replication status loaded: {status}")
        self.logger.info(f"time ago since last completed (hours): {status.get_last_completed_ago_hours()} h")

        self.assertIsNotNone(status.status,"replication status is None, that's not allowed")
        self.assertTrue(isinstance(status.status, ReplicationStatusEnum),
                        "replication status is not a valid ReplicationStatusModel enum value")
        self.assertTrue(status.get_last_completed_ago_hours() > 0 or status.get_last_completed_ago_hours() == -1,
                        "last completed replication should be more than 0 hours ago, or never be executed (-1)")

    def test_05_update_repository_replication(self) -> None:
        """ Update a repository replication """
        orig_repl_model: ReplicationModel = self._client.repository_replication.get(self.test_repo_key)
        repl_model: ReplicationModel = orig_repl_model.model_copy()
        self.logger.info(f"replication model loaded: {repl_model}")
        repl_model.enabled = not repl_model.enabled # invert the enabled status

        try:
            self._client.repository_replication.update(self.test_repo_key, repl_model)
        except Exception as e:
            self.fail(f"failed to update replication for repository 'test-pypi': {e}")

        self.assertNotEqual(self._client.repository_replication.get(self.test_repo_key).enabled, orig_repl_model.enabled,
                            "replication enabled status should be different after update")

        self._client.repository_replication.set(self.test_repo_key, orig_repl_model)
        self.logger.info(f"replication for repository 'test-pypi' restored to original state")

    def test_10_delete_create_repository_replication(self) -> None:
        """ Delete and create a repository replication """

        # TODO: define this at test data and not hardcoded here,
        #       because this is a real test and should be configurable
        cron_expression = "0 0 */12 * * ?"  # every 12 hours
        url = "https://trepo.intra.vsa.de/artifactory/test-pypi/"
        username = "admin"
        password = os.environ.get("ARTIFACTORY_04_ADMIN_PASSWORD", "<unknown>")

        manual_model: ReplicationModel = ReplicationModel()
        manual_model.username = username
        manual_model.password = password
        manual_model.url = url
        manual_model.cron_exp = cron_expression
        manual_model.enabled = True

        orig_repl_model: ReplicationModel = self._client.repository_replication.get(self.test_repo_key)
        self.assertIsNotNone(orig_repl_model, "original replication model is None")
        self.logger.info(f"replication model loaded: {orig_repl_model}")

        self._client.repository_replication.set(self.test_repo_key, manual_model)
        load_manual_model: ReplicationModel = self._client.repository_replication.get(self.test_repo_key)
        self.assertNotEqual(load_manual_model.cron_exp, orig_repl_model.cron_exp,
                            "replication cron expression should be different after creating new replication")

        try:
            self._client.repository_replication.delete(self.test_repo_key)
            self.logger.info(f"replication for repository 'test-pypi' deleted")
        except Exception as e:
            self.fail(f"failed to delete replication for repository 'test-pypi': {e}")

        try:
            self._client.repository_replication.get(self.test_repo_key)
            self.fail(f"failed to raise an exception on not existing replication for repository 'test-pypi'")
        except RepositoryNotFoundError:
            self.logger.info(f"RepositoryNotFoundError thrown as expected - this should happen!")

        try:
            self._client.repository_replication.set(self.test_repo_key, orig_repl_model)
            self.logger.info(f"replication for repository 'test-pypi' created")
        except Exception as e:
            self.fail(f"failed to create replication for repository 'test-pypi': {e}")

        try:
            self._client.repository_replication.get(self.test_repo_key)
            self.logger.info(f"replication for repository 'test-pypi' is recreated and exists again")
        except RepositoryNotFoundError:
            self.fail(f"repository 'test-pypi' should exist again, but can't be found after recreation of replication")

    def test_15_delete_create_repository_replication_remote(self) -> None:
        """ Delete and create a repository replication on a remote repository """

        repo_key = "remote-docker-neuvector"
        url = "https://repo.intra.vsa.de/artifactory/api/docker/remote-docker-neuvector"
        username = "admin"
        password = os.environ.get("ARTIFACTORY_03_ADMIN_PASSWORD", "<unknown>")
        cron_expression = "0 0 */12 * * ?"
        sync_artifact_properties = True




    def test_20_push_repository_replication(self) -> None:
        """ Push a repository replication """

        # TOOD: check this!

        repo_key = self.test_repo_key
        repo_key = "vsa-docker"


        try:
            self._client.repository_replication.trigger_replication(repo_key)
        except Exception as e:
            self.fail(f"failed to push replication for repository '{repo_key}': {e}")

        self.logger.info(f"replication for repository '{repo_key}' was pushed successfully")

    def test_50_manually(self) -> None:

        my_client = TestRepositoriesReplicationReal.CLIENT_TARGET
        all_repos: list[SimpleRepository] = my_client.repositories.list()

        for cur_repo in all_repos:
            if cur_repo.key == "remote-docker-neuvector":
                self.logger.info(f"found remote repository: {cur_repo.key}")
                try:
                    replication = my_client.repository_replication.get(cur_repo.key)
                    repo_details = my_client.repositories.get_repo(cur_repo.key)
                    # replication.enabled = False
                    # my_client.repository_replication.update(cur_repo.key, replication)
                    if replication is not None:
                        my_client.repository_replication.delete(cur_repo.key)
                    self.logger.info(f"replication for repository '{cur_repo.key}' exists: {replication}")
                except RepositoryNotFoundError:
                    self.logger.info(f"replication for repository '{cur_repo.key}' does not exist")
                except Exception as e:
                    self.fail(f"failed to check replication for repository '{cur_repo.key}': {e}")

    def test_enable_replication_remotes_from_source_artifactory(self) -> None:
        """
        Enable replication for all remote repositories at target Artifactory instance, from source Artifactory instance.

        TODO: find a solution to get the correct URLs, username and password if Main-Artifactory is broken.
        """
        source = TestRepositoriesReplicationReal.CLIENT_SOURCE
        target = TestRepositoriesReplicationReal.CLIENT_TARGET

        all_repos: list[SimpleRepository] = target.repositories.list()



        for cur_repo in all_repos:
            if RClassEnum(cur_repo.type.casefold()) == RClassEnum.remote:

                # if not cur_repo.key == "remote-docker-neuvector": # Docker
                # if not cur_repo.key == "remote-ext-ubuntu": # Debian
                # if not cur_repo.key == "remote-ext-http-owasp": # Generic
                # "remote-helm-helm" => only index
                # if not cur_repo.key == "remote-ext-jboss": # Maven
                if not cur_repo.key == "remote-helm-elastic": # Helm
                    continue

                self.logger.info(f"found remote repository: {cur_repo.key}")
                repo_details: RemoteRepositoryResponse = target.repositories.get_repo(cur_repo.key)
                try:
                    replication = target.repository_replication.get(cur_repo.key)
                    self.logger.info(f"replication for repository '{cur_repo.key}' exists, just adopt it.")
                    replication_exists = True
                except RepositoryNotFoundError:
                    self.logger.info(f"replication for repository '{cur_repo.key}' does not exist, add it")
                    replication_exists = False
                    replication = ReplicationModel()


                # 1. set the source for target repo to our source Artifactory instance
                # Bei DOCKER:
                # https://repo.intra.vsa.de/artifactory/api/docker/remote-docker-neuvector
                # Bei Debian:
                # https://repo.intra.vsa.de/artifactory/api/debian/remote-ext-ubuntu

                if repo_details.packageType is PackageTypeEnum.docker:
                    repo_details.url = f"{source.artifactory.url}/artifactory/api/{repo_details.packageType.value}/{repo_details.key}"
                else: # Debian
                    repo_details.url = f"{source.artifactory.url}/artifactory/{repo_details.key}"
                # pull replication needs username/password
                repo_details.username = "admin"
                repo_details.password = SecretStr(os.getenv("ARTIFACTORY_01_ADMIN_PASSWORD", "<not_set>"))

                # 2. enable the replication for target repo to our source Artifactory instance
                replication.enabled = True
                # the source url will be used from repository configuration!
                replication.cron_exp = "0 0 */12 * * ?"  # every 12 hours
                replication.sync_properties = True

                target.repositories.update_repo(repo_details)
                if replication_exists:
                    target.repository_replication.update(cur_repo.key, replication)
                else:
                    target.repository_replication.set(cur_repo.key, replication)

                target.repository_replication.trigger_replication(cur_repo.key)






if __name__ == '__main__':
    unittest.main()
