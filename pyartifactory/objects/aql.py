from __future__ import annotations

import logging

from pyartifactory.objects.object import ArtifactoryObject

logger = logging.getLogger("pyartifactory")

class ArtifactoryAQL(ArtifactoryObject):
    """
    Models an artifactory AQL query.

    URL: https://docs.jfrog.com/artifactory/docs/artifactory-query-language
    """

    # TODO: Implement the AQL query model with attributes and methods to construct and
    #       execute AQL queries against Artifactory.
