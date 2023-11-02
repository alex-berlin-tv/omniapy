import logging
from .model import ApiType, EditableAttributesResponse, MediaResultItem, Response, ResponseType, StreamType

import hashlib
from logging import Logger
from typing import Any, Optional, Type

import requests

BASE_URL: str = "https://api.nexx.cloud/v3.1/"
OMNIA_HEADER_X_REQUEST_CID: str = "X-Request-CID"
OMNIA_HEADER_X_REQUEST_TOKEN: str = "X-Request-Token"


class Omnia:
    def __init__(
        self,
        domain_id: str,
        api_secret: str,
        session_id: str,
        logger: Logger = logging.getLogger(),
    ):
        self.domain_id = domain_id
        self.api_secret = api_secret
        self.session_id = session_id
        self.logger = logger

    def by_id(
        self,
        stream_type: StreamType,
        item_id: int,
        parameters: dict[str, str] = {},
    ) -> Response[MediaResultItem]:
        """Return a item of a given stream type by it's id."""
        return self.call(
            "get",
            stream_type,
            ApiType.MEDIA,
            "byid",
            [str(item_id)],
            parameters,
            MediaResultItem,
        )
    
    def update(
        self,
        stream_type: StreamType,
        item_id: int,
        parameters: dict[str, str],
    ) -> Response[Any]:
        """
        Will update the general Metadata of a Media Item. Uses the Management API.
        """
        return self.call(
            "put",
            stream_type,
            ApiType.MANAGEMENT,
            "update",
            [str(item_id)],
            parameters,
            Any,
        )

    def upload_by_url(
        self,
        stream_type: StreamType,
        url: str,
        use_queue: bool,
        filename: Optional[str] = None,
    ) -> Response[Any]:
        """
        will create a new Media Item of the given Streamtype, if the given
        urlParameter contains a valid Source for the given Streamtype.
        """
        data = {
            "url": url,
            "useQueue": 1 if use_queue else 0,
        }
        if filename:
            data["filename"] = filename
        return self.call(
            "post",
            stream_type,
            ApiType.MANAGEMENT,
            "fromurl",
            [],
            data,
            Any,
        )

    def editable_attributes(
        self,
        stream_type: StreamType,
    ) -> Response[EditableAttributesResponse]:
        """
        Lists all editable attributes for a given stream type. Documentation can be found here:
        https://api.nexx.cloud/v3.1/system/editablerestrictionsfor/:streamtype
        
        This method is needed as there is no other documentation of all the available metadata
        fields in omnia. Especially useful if you want to know which metadata attributes
        you can alter using the `omnia.update` method.
        """
        return self.call(
            "get",
            stream_type,
            ApiType.SYSTEM,
            "editableattributesfor",
            [stream_type.value],
            {},
            EditableAttributesResponse,
        )

    def call(
        self,
        method: str,
        stream_type: StreamType,
        api_type: ApiType,
        operation: str,
        args: list[str],
        parameters: dict[str, str],
        response_type: Type[ResponseType],
    ) -> Response[ResponseType]:
        """Generic call to the omnia API."""
        return self.__universal_call(
            method, stream_type, api_type, operation, args, parameters, response_type
        )

    def __universal_call(
        self,
        method: str,
        stream_type: StreamType,
        api_type: ApiType,
        operation: str,
        args: list[str],
        parameters: dict[str, str],
        response_type: Type[ResponseType],
    ) -> Response[ResponseType]:
        args_str = "/".join(args)
        url: str = ""
        if api_type is ApiType.MEDIA:
            url = self.__url_builder(
                BASE_URL, self.domain_id, stream_type.value, operation, args_str)
        elif api_type is ApiType.MANAGEMENT:
            url = self.__url_builder(
                BASE_URL, self.domain_id, "manage", stream_type.value, args_str, operation)
        elif api_type is ApiType.UPLOAD_LINK_MANAGEMENT:
            url = self.__url_builder(
                BASE_URL, self.domain_id, "manage", "uploadlinks", operation)
        elif api_type is ApiType.SYSTEM:
            url = self.__url_builder(
                BASE_URL, self.domain_id, "system", operation, args_str)
        header = self.__request_header(
            operation, self.domain_id, self.api_secret, self.session_id)
        self.logger.debug(
            f"About to send {method} to {url} with header {header} and params {parameters}")
        result = requests.request(
            method,
            headers=header,
            url=url,
            data=parameters,
        )
        return Response[response_type].model_validate(result.json())

    def __request_header(
        self,
        operation: str,
        domain_id: str,
        api_secret: str,
        session_id: str,
    ) -> dict[str, str]:
        signature = hashlib.md5(
            f"{operation}{domain_id}{api_secret}".encode("utf-8"))
        return {
            OMNIA_HEADER_X_REQUEST_CID: session_id,
            OMNIA_HEADER_X_REQUEST_TOKEN: signature.hexdigest(),
        }

    @staticmethod
    def __url_builder(*args) -> str:
        rsl: list[str] = []
        for arg in args:
            rsl.append(str(arg).lstrip("/").rstrip("/"))
        return "/".join(rsl)
