from fastapi import APIRouter

from ..models.responses import PingResponse

router = APIRouter(prefix='/api/v1', tags=['API v1'])


@router.get('/ping', response_model=PingResponse)
async def ping():
    return PingResponse(message='pong', version='1.0.0')
