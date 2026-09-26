"""Telegram Bot API MCP Server."""

from __future__ import annotations

from typing import Optional

from fastmcp import FastMCP
from pydantic import Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from app.services.telegram_service import TelegramError, TelegramService
from app.capability_bind import bind_declared_capabilities

mcp = FastMCP(
    name="telegram",
    instructions="Telegram Bot API. Vault bundle is {token}. Sends require confirm=true.",
)

_CREDS_JSON = Field(default=None, description="Bot token JSON from Studio vault inject")
_CREDS_PATH = Field(default=None, description="Local credentials JSON path")


def _creds_required() -> dict:
    return {
        "error_code": "CREDENTIALS_REQUIRED",
        "error_message": "Provide credentials_path or credentials_json",
        "retryable": False,
        "original_provider_error": None,
    }


def _confirm_required() -> dict:
    return {
        "error_code": "CONFIRM_REQUIRED",
        "error_message": "Set confirm=true to execute this side-effecting tool",
        "retryable": False,
        "original_provider_error": None,
    }


@mcp.tool()
def telegram_send_message(
    chat_id: str = Field(..., description="Chat id or @username"),
    text: str = Field(..., description="Message text", json_schema_extra={"x-datumbridge-encoding": "plain"}),
    credentials_path: Optional[str] = _CREDS_PATH,
    credentials_json: Optional[str] = _CREDS_JSON,
    confirm: bool = Field(default=False),
    dry_run: bool = Field(default=False),
) -> dict:
    """Send a Telegram message. Requires confirm=true.

        Capabilities: telegram.telegram_send_message
Outputs: success
        """
    try:
        if not credentials_path and not credentials_json:
            return {"success": False, "error": _creds_required()}
        if dry_run:
            return {"success": True, "dry_run": True, "message": "Would send message", "chat_id": chat_id}
        if not confirm:
            return {"success": False, "error": _confirm_required()}
        result = TelegramService(credentials_json, credentials_path).send_message(chat_id, text)
        return {"success": True, "message": "Sent", "result": result}
    except TelegramError as e:
        return {"success": False, "error": e.to_dict()}


@mcp.tool()
def telegram_get_updates(
    credentials_path: Optional[str] = _CREDS_PATH,
    credentials_json: Optional[str] = _CREDS_JSON,
    limit: int = Field(default=20),
    offset: Optional[int] = Field(default=None),
) -> dict:
    """Get recent Telegram bot updates (long-poll replacement for v1).

        Capabilities: telegram.telegram_get_updates
Outputs: success
        """
    try:
        if not credentials_path and not credentials_json:
            return {"success": False, "error": _creds_required()}
        updates = TelegramService(credentials_json, credentials_path).get_updates(limit, offset)
        return {"success": True, "updates": updates, "total_count": len(updates)}
    except TelegramError as e:
        return {"success": False, "error": e.to_dict()}



bind_declared_capabilities(mcp)

_base_app = mcp.http_app()


async def health(_request):
    return JSONResponse({"status": "ok", "service": "telegram-mcp"})


http_app = Starlette(
    routes=[Route("/health", health), Mount("/", _base_app)],
    lifespan=getattr(_base_app, "lifespan", None),
)

if __name__ == "__main__":
    mcp.run()
