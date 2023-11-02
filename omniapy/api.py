from .model import ApiType, Response, StreamType

import hashlib
from logging import Logger
from typing import Optional

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
        logger: Logger,
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
    ):
        """Return a item of a given stream type by it's id."""
        return self.call(
            "get",
            stream_type,
            ApiType.MEDIA,
            "byid",
            [str(item_id)],
            parameters,
        )
    
    def update(
        self,
        stream_type: StreamType,
        item_id: int,
        parameters: dict[str, str],
    ):
        """
        Will update the general Metadata of a Media Item. Uses the Management API.
        """
        return self.call(
            "put",
            stream_type,
            ApiType.MANAGEMENT,
            "update",
            [str(item_id)],
            parameters
        )

    def upload_by_url(
        self,
        stream_type: StreamType,
        url: str,
        use_queue: bool,
        filename: Optional[str] = None,
    ):
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
            data
        )

    def call(
        self,
        method: str,
        stream_type: StreamType,
        api_type: ApiType,
        operation: str,
        args: list[str],
        parameters: dict[str, str]
    ) -> Response:
        """Generic call to the Omnia Media API. Won't work with the management API's."""
        return self.__universal_call(
            method, stream_type, api_type, operation, args, parameters
        )

    def __universal_call(
        self,
        method: str,
        stream_type: StreamType,
        api_type: ApiType,
        operation: str,
        args: list[str],
        parameters: dict[str, str],
    ) -> Response:
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
        print(result.json())
        return Response.model_validate(result.json())

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
