from fastapi import APIRouter, HTTPException, status

from app.models.job_application import (
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
)
from app.services import job_application_service as svc

router = APIRouter(
    prefix='/api/v1/applications',
    tags=['Job Applications'],
)


@router.post(
    '',
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(data: JobApplicationCreate):
    return svc.create_application(data)


@router.get(
    '',
    response_model=list[JobApplicationResponse],
)
def list_applications():
    return svc.list_applications()


@router.get(
    '/{app_id}',
    response_model=JobApplicationResponse,
)
def get_application(app_id: str):
    app = svc.get_application(app_id)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application {app_id} not found',
        )
    return app


@router.patch(
    '/{app_id}',
    response_model=JobApplicationResponse,
)
def update_application(app_id: str, data: JobApplicationUpdate):
    app = svc.update_application(app_id, data)
    if app is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application {app_id} not found',
        )
    return app


@router.delete(
    '/{app_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_application(app_id: str):
    existed = svc.delete_application(app_id)
    if not existed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application {app_id} not found',
        )
