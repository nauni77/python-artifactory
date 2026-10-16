from __future__ import annotations

import logging

from pyartifactory import Artifactory
from pyartifactory.models.artifact import ArtifactListResponse, ArtifactListFileResponse, ArtifactListFolderResponse
from pyartifactory.tests.base_test_real import TestBaseReal


class TestArtifactsReal(TestBaseReal):


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logger.info("setting up the test class for TestArtifactsReal")
        cls.logger = logging.getLogger("pyartifactory_artifact_real")
        cls._client: Artifactory = TestArtifactsReal.CLIENT_DEFAULT

    @staticmethod
    def create_files_map(artifact_list: ArtifactListResponse) -> tuple[dict[str, ArtifactListFileResponse],
                                                                        dict[str, ArtifactListFolderResponse]]:
        """
        Creates a map of files from the artifact list.
        :param artifact_list: The artifact list response from Artifactory.
        :return: A dictionary mapping file paths to their corresponding ArtifactoryItem objects.
        """
        files_map: dict[str, ArtifactListFileResponse] = {}
        folders_map: dict[str, ArtifactListFolderResponse] = {}
        for file in artifact_list.files:
            match file:
                case ArtifactListFileResponse():
                    files_map[file.uri] = file
                case ArtifactListFolderResponse():
                    folders_map[file.uri] = file
                case _:
                    raise Exception(f"Unknown artifact type: {type(file)}")

        return files_map, folders_map

    def test_01_list_artifacts(self) -> None:
        """
        TODO: do this after synchronizing user, groups and permissions
        Just list artifacts in a repository and check if the response is valid.
        Options are "listFolders", "deep", "depth", "includeRootPath", ...
        """
        ...

    def test_02_load_and_store_artefact(self) -> None:
        """
        TODO: do this after synchronizing user, groups and permissions
        Uploads and file and downloads it again to check if the file is the same.
        """
        client: Artifactory = self._client
        # TODO: this is not working - switch to retrieve
        filename = client.artifacts.download("remote-ext-mavencentral-cache/com/cybozu/labs/langdetect/1.1-20120112/langdetect-1.1-20120112-sources.jar")
        print(f"Downloaded file: {filename}")

        ## Dies kommt bei einem Proxy/Remote Repository,
        ## wenn das Artefakt nicht mehr im Remote Repository vorhanden ist oder lange nicht mehr abgerufen wurde.
        # {
        #     "errors": [
        #         {
        #             "status": 404,
        #             "message": "Resource has expired"
        #         }
        #     ]
        # }

        # Proxy/Remotes können keine Deploy erhalten.
        # client_target.artifacts.upload(
        #     "./spring-boot-starter-amqp-3.0.0-SNAPSHOT-sources.jar",
        #     "/org/springframework/boot/spring-boot-starter-amqp/3.0.0-SNAPSHOT/spring-boot-starter-amqp-3.0.0-SNAPSHOT-sources.jar")


