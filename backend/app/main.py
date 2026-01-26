from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .config import settings
from .db.dynamodb import create_table_if_not_exists
from .routers import health, api_v1, job_applications


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_table_if_not_exists()
    yield


app = FastAPI(
    title=settings.app_name,
    docs_url='/api/docs',
    redoc_url='/api/redoc',
    openapi_url='/api/openapi.json',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health.router)
app.include_router(api_v1.router)
app.include_router(job_applications.router)

# AWS Lambda handler
handler = Mangum(app, lifespan='off')
