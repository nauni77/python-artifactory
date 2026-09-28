from typing import Annotated, Any

from pydantic import BaseModel, Field, BeforeValidator

def parse_formatted_int(value: Any) -> Any:
    """Convert numbers such as '2,969,847' to integers."""
    if isinstance(value, str):
        return int(value.replace(",", ""))
    return value

FormattedInt = Annotated[int, BeforeValidator(parse_formatted_int)]

class RepositoryStorageSummary(BaseModel):
    """Models repository storage summary."""
    repo_key: str = Field(alias="repoKey")
    repo_type: str = Field(alias="repoType")
    folders_count: FormattedInt = Field(alias="foldersCount")
    files_count: FormattedInt = Field(alias="filesCount")
    used_space: str = Field(alias="usedSpace")
    used_space_in_bytes: FormattedInt = Field(alias="usedSpaceInBytes")
    items_count: FormattedInt = Field(alias="itemsCount")
    package_type: str | None = Field(alias="packageType", default=None)
    percentage: str | None = Field(alias="percentage", default=None)

class FileStoreSummary(BaseModel):
    """Models file store summary."""
    storage_type: str = Field(alias="storageType")
    storage_directory: str = Field(alias="storageDirectory")
    total_space: str = Field(alias="totalSpace")
    used_space: str = Field(alias="usedSpace")
    free_space: str = Field(alias="freeSpace")

class BinariesSummary(BaseModel):
    """Models binaries summary."""
    binaries_count: FormattedInt = Field(alias="binariesCount")
    binaries_size: str = Field(alias="binariesSize")
    artifacts_size: str = Field(alias="artifactsSize")
    optimization: str = Field(alias="optimization")
    items_count: FormattedInt = Field(alias="itemsCount")
    artifacts_count: FormattedInt = Field(alias="artifactsCount")

class StorageInfo(BaseModel):
    """Models storage information."""

    file_store_summary: FileStoreSummary = Field(alias="fileStoreSummary")
    binaries_summary: BinariesSummary = Field(alias="binariesSummary")
    repositories_summary_list: list[RepositoryStorageSummary] = Field(alias="repositoriesSummaryList")
