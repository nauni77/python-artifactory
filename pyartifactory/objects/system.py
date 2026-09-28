from __future__ import annotations

import datetime
import logging

import requests
from requests.exceptions import ConnectionError

from pyartifactory.enums import ServiceType
from pyartifactory.exception import handle_exception
from pyartifactory.models.system import StorageInfo
from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")


class ArtifactorySystem(ArtifactoryObject):
    """Models artifactory system requests."""

    """ 
    TODO: add methods for token management
    https://docs.jfrog.com/artifactory/reference/createorrefreshtoken
    https://docs.jfrog.com/artifactory/reference/gettokeninfos
    https://docs.jfrog.com/artifactory/reference/revoketoken
    """

    _uri = "system"
    _tokens_uri = "tokens"
    _artifactory_uri = "artifactory"

    def artifactory_ping(self) -> bool:
        """
        Since: 2.3.0
        Ping the artifactory instance to check if it's alive.
        :return: True if artifactory instance is alive, False otherwise
        """
        try:
            response = self._get(f"artifactory/api/{self._uri}/ping", raise_for_status=False)
            if response.status_code == 200:
                logger.debug("Artifactory ping successful")
                return True
            logger.error("Artifactory ping failed with status code %s", response.status_code)
            return False
        except ConnectionError as ce:
            logger.error("Artifactory ping failed: %s", ce)
            return False

    def readiness_probe(self) -> bool:
        """
        Since: 7.31.x
        Check if the artifactory instance is ready to serve requests.
        :return: True if artifactory instance is ready, False otherwise
        """
        try:
            # json response: {"code" : "OK"}
            response = self._get(f"artifactory/api/v1/{self._uri}/readiness", raise_for_status=False)
            if response.status_code == 200:
                logger.debug("Artifactory readiness probe successful")
                return True
            logger.error("Artifactory readiness probe failed with status code %s", response.status_code)
            return False
        except ConnectionError as ce:
            logger.error("Artifactory readiness probe failed: %s", ce)
            return False

    def liveness_probe(self) -> bool:
        """
        Since: 7.31.x
        Check if the artifactory instance is alive.
        :return: True if artifactory instance is alive, False otherwise
        """
        try:
            # json response: {"code" : "OK"}
            response = self._get(f"artifactory/api/v1/{self._uri}/liveness", raise_for_status=False)
            if response.status_code == 200:
                logger.debug("Artifactory liveness probe successful")
                return True
            logger.error("Artifactory liveness probe failed with status code %s", response.status_code)
            return False
        except ConnectionError as ce:
            logger.error("Artifactory liveness probe failed: %s", ce)
            return False

    def get_artifactory_version(self) -> str:
        """
        Since: 2.2.2
        Get version of the artifactory instance.
        :return: version of artifactory instance as string
        """
        response = self._get(f"artifactory/api/{self._uri}/version")
        logger.debug("Artifactory version successfully retrieved")
        return response.json().get("version")


    def get_system_info(self) -> str:
        """
        Since: 2.2.0
        Get system information of the artifactory instance.
        :return: system information of artifactory instance as dict
        """
        response = self._get(f"artifactory/api/{self._uri}")
        logger.debug("Artifactory system information successfully retrieved")
        # yes, it's just plain text, not JSON, so we return the text content
        return response.text

    def get_license_information(self) -> dict[str, str]:
        """
        Since: 3.3.0
        Return information about the currently installed license.
        url: https://docs.jfrog.com/administration/reference/installlicense

        :return: license information of artifactory instance as dict
        """
        response = self._get(f"artifactory/api/{self._uri}/license")
        logger.debug("Artifactory license information successfully retrieved")
        # yes, it's just plain text, not JSON, so we return the text content
        dict_license: dict[str, str] = response.json()
        valid_through = datetime.datetime.strptime(dict_license["validThrough"], "%b %d, %Y").date()
        remaining_days = (valid_through - datetime.date.today()).days
        dict_license["remainingDays"] = str(remaining_days)
        return dict_license

    def install_license(self, license_key: str) -> None:
        """
        Since: 3.3.0
        Install a new license key on the artifactory instance.
        url: https://docs.jfrog.com/administration/reference/installlicense

        :param license_key: license key to install
        :return: None
        :raises: ArtifactoryError if the license installation fails
        """
        payload = {"licenseKey": license_key}
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        try:
            self._post(f"artifactory/api/{self._uri}/license", json=payload, headers=headers, raise_for_status=False)
            logger.debug("Artifactory license key successfully installed")
        except requests.exceptions.HTTPError as error:
            handle_exception(error, "Artifactory license key installation failed", ServiceType.SYSTEM)


    def get_background_tasks(self) -> list[dict[str, str]]:
        """
        Since: 3.3.0
        Get a list of background tasks currently running on the artifactory instance.
        url: https://docs.jfrog.com/administration/reference/backgroundtasks

        :return: list of background tasks as dict
        """
        response = self._get(f"{self._artifactory_uri}/api/tasks")
        logger.debug("Artifactory background tasks successfully retrieved")
        return response.json()

    def get_storage_summary_info(self) -> StorageInfo:
        """
        Since: 3.3.0
        Get storage summary information of the artifactory instance.
        url: https://docs.jfrog.com/artifactory/reference/getstoragesummaryinfo

        :return: storage summary information of artifactory instance as dict
        """
        response = self._get(f"{self._artifactory_uri}/api/storageinfo",
                             headers={"accept": "application/json"})
        logger.debug("Artifactory storage summary information successfully retrieved")

        return StorageInfo.model_validate(response.json())

    def refresh_storage_summary_info(self) -> bool:
        """
        Since: 3.3.0
        Refresh storage summary information of the artifactory instance.
        url: https://docs.jfrog.com/artifactory/reference/refreshstoragesummaryinfo

        :return: True if the storage summary information was successfully scheduled for refresh,
                 False otherwise
        """
        response = self._post(f"{self._artifactory_uri}/api/storageinfo/calculate",
                              headers={"accept": "application/json"})
        logger.debug(f"{response.text}")

        if response.status_code == 202:
            return True
        else:
            return False
