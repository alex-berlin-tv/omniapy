from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, TypeVar


from pydantic import BaseModel, Field, RootModel


class Bool(int, Enum):
    """
    A boolean value is expressed as a 0 for `false` and 1 for `true`.
    String is used as type as it's not possible to nil integer values
    (which is needed in order to omit unset parameters as the query parameter).
    """

    FALSE = 0
    TRUE = 1

    def to_bool(self) -> bool:
        if self is self.FALSE:
            return False
        return True


class StreamType(str, Enum):
    # Streamtypes represent the different types of media items.
    ALL = "allmedia"
    VIDEO = "videos"
    AUDIO = "audio"
    SHOW = "shows"
    RADIO = "radio"
    LIVE = "live"


class ApiType(str, Enum):
    MEDIA = "media"
    MANAGEMENT = "management"
    UPLOAD_LINK_MANAGEMENT = "upload_link_management"
    SYSTEM = "system"
    DOMAIN = "domain"


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
    """
    MediaResultGeneral provides general information about a media item, including
    its ID, title, and more.

    Some fields (like Channel) are optional (or as omnia calls them »additional«)
    fields. You have to use the »additionalFields« parameter for the request.
    """
    item_id: int = Field(alias="ID")
    gid: int = Field(alias="GID")
    hash_value: str = Field(alias="hash")
    title: str = Field(alias="title")
    subtitle: str = Field(alias="subtitle")
    genre_raw: Optional[str] = Field(None, alias="genre_raw")
    genre: Optional[str] = Field(None, alias="genre")
    content_moderation_aspects: str = Field(alias="contentModerationAspects")
    uploaded: Optional[datetime] = Field(None, alias="uploaded")
    created: datetime = Field(alias="created")
    audio_type: Optional[str] = Field(None, alias="audiotype")
    runtime: Optional[str] = Field(None, alias="runtime")
    is_picked: Optional[Bool] = Field(None, alias="isPicked")
    for_kids: Optional[Bool] = Field(None, alias="forKids")
    is_pay: Bool = Field(alias="isPay")
    is_ugc: Optional[Bool] = Field(None, alias="isUGC")


class ManagementResult(BaseModel):
    message: str


class MediaResultItem(BaseModel):
    """
    MediaResultItem holds detailed information about a single media result item.
    """
    general: MediaResultGeneral = Field(alias="general")
    # image_data: MediaResultImageData = Field(alias="imagedata")
    image_data: Any = Field(alias="imagedata")


class MediaResult(RootModel):
    """
    MediaResult is a collection of MediaResultItem instances, each representing
    a media result. The decision for using a dedicated type for a List of
    `MediaResultItem`s was made to ease the further work with results outside
    this package.
    """
    root: list[MediaResultItem]


class EditableAttributesProperties(BaseModel):
    """
    EditableAttributesResponse is a map that associates attribute names with their
    editable properties.
    """
    attrib_type: str = Field(alias="type")
    max_length: Optional[int] = Field(None, alias="maxlength")
    attrib_format: Optional[str] = Field(None, alias="format")
    hint: Optional[str] = None
    allowed_in_ugc: Bool = Field(alias="allowedInUGC")


class EditableAttributesResponse(RootModel):
    """
    EditableAttributesResponse is a map that associates attribute names with their
    editable properties.
    """
    root: dict[str, EditableAttributesProperties]


ResponseType = TypeVar("ResponseType")


class Response(BaseModel, Generic[ResponseType]):
    """
    Response represents the response structure obtained from a nexxOmnia
    API call. It encapsulates the metadata, result, and paging information
    as documented here https://api.docs.nexx.cloud/api-design/response-object.
    """
    metadata: ResponseMetadata
    result: Optional[ResponseType] = None
    paging: Optional[ResponsePaging] = None
