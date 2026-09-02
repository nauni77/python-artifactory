from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

class ReplicationStatusEnum(Enum):
    """ Enum of all possible states of a replication """
    unknown = "unknown"
    never_run = "never_run"
    incomplete = "incomplete"
    error = "error"
    warn = "warn"
    ok = "ok"
    inconsistent = "inconsistent"
    partial_failure = "partial_failure"

class ReplicationStatusModel(BaseModel):
    """
    Models a base repository replication status.
    This can also retrieve separate information about more replications,
    but our Artifactory Pro only support one replication target.
    So we for now only support one replication on each repository.
    """
    status: ReplicationStatusEnum
    last_completed: datetime | None = Field(default=None, alias="lastCompleted")
    # targets and repositories are not supported for now, because Artifactory Pro just support one replication taget.

    def get_last_completed_ago_hours(self) -> float:
        if self.last_completed is None:
            return -1
        return round((datetime.now(self.last_completed.tzinfo) - self.last_completed).total_seconds() / 3600, 2)



class ReplicationModel(BaseModel):
    """Models a repository replication"""
    enabled: bool = True  # whether replication is enabled

    repo_key: str | None = Field(default=None, alias="repoKey", exclude=True) # key of the repository to replicate
    replication_key: str | None = Field(default=None, alias="replicationKey", exclude=True) # key of the replication configuration
    url: str | None = None # URL of the remote repository to replicate to

    socket_timeout_millis: int | None = Field(default=None, alias="socketTimeoutMillis") # milliseconds

    username: str | None = None # login at remote
    password: str | None = None # login password at remote

    enable_event_replication: bool | None = Field(default=None, alias="enableEventReplication") # refers to both push and pull replication

    cron_exp: str | None = Field(default=None, alias="cronExp") # Cron expression for scheduled replication

    sync_deletes: bool = Field(default=False, alias="syncDeletes") # Whether to sync deletions(default false)
    sync_properties: bool = Field(default=True, alias="syncProperties") # Whether to sync properties(default true)
    sync_statistics: bool | None = Field(default=None, alias="syncStatistics") # Whether to sync statistics

    include_path_prefix_pattern: str | None = Field(default=None, alias="includePathPrefixPattern") # Include path prefix pattern(added in Artifactory 7.24.4)
    exclude_path_prefix_pattern: str | None = Field(default=None, alias="excludePathPrefixPattern") # Exclude path prefix pattern(added in Artifactory 7.24.4)

    proxy: str | None = None # id of proxy configuration
    disable_proxy: bool = Field(default=True, alias="disableProxy") # When true, disables proxy usage for this replication

    check_binary_existence_in_filestore: bool | None = Field(default=None, alias="checkBinaryExistenceInFilestore") # When true, enables distributed checksum storage (requires Enterprise+ license)
