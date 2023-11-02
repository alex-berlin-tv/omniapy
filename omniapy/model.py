from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union


from pydantic import BaseModel, Field


class Bool(int, Enum):
    FALSE = 0
    TRUE = 1

    def to_bool(self) -> bool:
        if self is self.FALSE:
            return False
        return True


class ResponseMetadata(BaseModel):
    """Metadata part of an API response."""

    status: int = Field(alias="status")
    """The HTTP Status for this Call."""
    api_version: Optional[str] = Field(None, alias="apiversion")
    """Version of the API."""
    verb: str = Field(alias="verb")
    """The used HTTP Verb."""
    processing_time: float = Field(alias="processingtime")
    """Internal Duration, needed to create the response."""
    called_with: Optional[str] = Field(None, alias="calledwith")
    """The called Endpoint and Parameter."""
    called_for: Optional[str] = Field(None, alias="calledfor")
    """The `cfo` Parameter from the API Call."""
    for_domain: Optional[int] = Field(None, alias="fordomain")
    """The calling Domain ID."""
    from_stage: Optional[int] = Field(None, alias="fromstage")
    """The result was created by a Stage or Productive Server."""
    notice: Optional[str] = Field(None, alias="notice")
    """
    If the Call uses deprecated Functionality, find here a Hint, what Attributes
    should be changed.
    """
    error_hint: Optional[str] = Field(None, alias="errorhint")
    """If the Call failed, a Hint for the Failure Reason."""
    from_cache: Optional[int] = Field(None, alias="fromcache")
    """States whether result came from cache"""

    class Config:
        populate_by_name = True


class ResponsePaging(BaseModel):
    """Information on the paging of an result."""

    start: int = Field(alias="start")
    """The Start of the Query Range."""
    limit: int = Field(alias="limit")
    """The given maximal Item List Length."""
    result_count: int = Field(alias="resultcount")
    """The maximally available Number of Items."""

    class Config:
        populate_by_name = True


class MediaResultGeneral(BaseModel):
    item_id: int = Field(alias="ID")
    gid: int = Field(alias="GID")
    hash_value: str = Field(alias="hash")
    title: str = Field(alias="title")
    subtitle: str = Field(alias="subtitle")
    genre_raw: str = Field(alias="genre_raw")
    genre: str = Field(alias="genre")
    content_moderation_aspects: str = Field(alias="contentModerationAspects")
    uploaded: datetime = Field(alias="uploaded")
    created: datetime = Field(alias="created")
    audio_type: str = Field(alias="audiotype")
    runtime: str = Field(alias="runtime")
    is_picked: Bool = Field(alias="isPicked")
    for_kids: Bool = Field(alias="forKids")
    is_pay: Bool = Field(alias="isPay")
    is_ugc: Bool = Field(alias="isUGC")


class ManagementResult(BaseModel):
    message: str


class MediaResult(BaseModel):
    general: MediaResultGeneral = Field(alias="general")
    # image_data: MediaResultImageData = Field(alias="imagedata")
    image_data: Any = Field(alias="imagedata")


class Response(BaseModel):
    metadata: ResponseMetadata
    result: Union[
        ManagementResult,
        MediaResult,
        list[MediaResult],
        None
    ] = None
    paging: Optional[ResponsePaging] = None


class StreamType(str, Enum):
    VIDEO = "videos"
    AUDIO = "audio"
    SHOW = "shows"


class ApiType(str, Enum):
    MEDIA = "media"
    MANAGEMENT = "management"
    UPLOAD_LINK_MANAGEMENT = "upload_link_management"
    SYSTEM = "system"
    DOMAIN = "domain"
