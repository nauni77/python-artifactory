from __future__ import annotations

import datetime
import logging
from datetime import UTC

from pyartifactory.exception import InvalidTokenDataError
from pyartifactory.models.auth import AccessTokenModel, ApiKeyModel, PasswordModel
from pyartifactory.objects.object import ArtifactoryObject
from requests.exceptions import ConnectionError

logger = logging.getLogger("pyartifactory")


class ArtifactorySystem(ArtifactoryObject):
    """Models artifactory system requests."""

    _uri = "system"
    _tokens_uri = "tokens"

    def artifactory_ping(self) -> bool:
        """
        Since: 2.3.0
        Ping the artifactory instance to check if it's alive.
        :return: True if artifactory instance is alive, False otherwise
        """
        try:
            response = self._get(f"api/{self._uri}/ping", raise_for_status=False)
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
            response = self._get(f"api/v1/{self._uri}/readiness", raise_for_status=False)
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
            response = self._get(f"api/v1/{self._uri}/liveness", raise_for_status=False)
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
        response = self._get(f"api/{self._uri}/version")
        logger.debug("Artifactory version successfully retrieved")
        return response.json().get("version")


    def get_system_info(self) -> str:
        """
        Since: 2.2.0
        Get system information of the artifactory instance.
        :return: system information of artifactory instance as dict
        """
        response = self._get(f"api/{self._uri}")
        logger.debug("Artifactory system information successfully retrieved")
        # yes, it's just plain text, not JSON, so we return the text content
        return response.text

    def get_license_information(self) -> dict[str, str]:
        """
        Since: 3.3.0
        Return information about the currently installed license.
        :return: license information of artifactory instance as dict
        """
        response = self._get(f"api/{self._uri}/license")
        logger.debug("Artifactory license information successfully retrieved")
        # yes, it's just plain text, not JSON, so we return the text content
        dict_license: dict[str, str] = response.json()
        valid_through = datetime.datetime.strptime(dict_license["validThrough"], "%b %d, %Y").date()
        remaining_days = (valid_through - datetime.date.today()).days
        dict_license["remainingDays"] = str(remaining_days)
        return dict_license

    def install_license(self, license_key: str) -> bool:
        """
        Since: 3.3.0
        Install a new license key on the artifactory instance.
        :param license_key: license key to install
        :return: True if license key was installed successfully, False otherwise
        """
        payload = {"licenseKey": license_key}
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        response = self._post(f"api/{self._uri}/license", json=payload, headers=headers, raise_for_status=False)
        if response.status_code == 200:
            logger.debug("Artifactory license key successfully installed")
            return True
        logger.error("Artifactory license key installation failed with status code %s", response.status_code)
        return False