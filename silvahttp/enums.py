from enum import Enum


class Methods(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    TRACE = "TRACE"
    CONNECT = "CONNECT"
