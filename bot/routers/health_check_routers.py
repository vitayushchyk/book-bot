from fastapi import APIRouter, status
from starlette.responses import JSONResponse

health_check_router = APIRouter(tags=["Healthcheck"])


@health_check_router.get(
    "/health-check/",
    status_code=status.HTTP_200_OK,
    description="Healthcheck endpoint to check the health of the application.",
)
async def _health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=dict(detail="Application is healthy.")
    )
