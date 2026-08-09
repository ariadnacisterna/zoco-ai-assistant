from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_health_service
from app.core.constants import HEALTH_PATH, HEALTH_TAG
from app.core.enums import ServiceStatus
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter(tags=[HEALTH_TAG])


@router.get(
    HEALTH_PATH,
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": HealthResponse},
    },
)
async def get_health(
    response: Response,
    health_service: Annotated[
        HealthService,
        Depends(get_health_service),
    ],
) -> HealthResponse:
    """Return the current application health status."""

    health_status = await health_service.get_health_status()

    if health_status.status == ServiceStatus.ERROR:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
