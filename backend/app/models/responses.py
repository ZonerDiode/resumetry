from .base import BaseSchema


class HealthResponse(BaseSchema):
    status: str
    service: str


class PingResponse(BaseSchema):
    message: str
    version: str


class ErrorResponse(BaseSchema):
    detail: str
