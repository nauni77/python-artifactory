from __future__ import annotations

import logging

from pyartifactory.tests.base_test_real import TestBaseReal

from pyartifactory import Artifactory
from pyartifactory.models.artifact import ArtifactListResponse, ArtifactListFileResponse, ArtifactListFolderResponse


class TestAQLReal(TestBaseReal):


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.logger.info("setting up the test class for TestArtifactsReal")
        cls.logger = logging.getLogger("pyartifactory_artifact_real")
        cls._client: Artifactory = TestAQLReal.CLIENT_DEFAULT

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

