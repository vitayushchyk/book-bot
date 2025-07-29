from fastapi import APIRouter, HTTPException, Request, status
from starlette.responses import JSONResponse
from telegram import Update

webhook_router = APIRouter(tags=["Webhook"])


@webhook_router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    description="Telegram webhook endpoint to receive updates from Telegram.",
)
async def telegram_webhook(request: Request):

    try:
        data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON"
        )
    telegram_application = request.app.state.telegram_application
    update = Update.de_json(data, telegram_application.bot)
    await telegram_application.process_update(update)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=dict(detail="Webhook received and processed successfully"),
    )
