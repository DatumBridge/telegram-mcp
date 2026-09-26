"""Telegram Bot API client. Bot token from Studio vault."""

from __future__ import annotations

import json
from typing import Any, Optional

import requests


class TelegramError(Exception):
    def __init__(self, message: str, error_code: str = "TELEGRAM_ERROR", retryable: bool = False):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "error_message": str(self),
            "retryable": self.retryable,
            "original_provider_error": None,
        }


def _token(credentials_json: Optional[str], credentials_path: Optional[str]) -> str:
    data: dict[str, Any] = {}
    if credentials_json:
        data = json.loads(credentials_json)
    elif credentials_path:
        with open(credentials_path, encoding="utf-8") as fh:
            data = json.load(fh)
    token = (data.get("token") or data.get("access_token") or "").strip()
    if not token:
        raise TelegramError(
            "Credentials required: bot token",
            error_code="CREDENTIALS_REQUIRED",
        )
    return token


class TelegramService:
    def __init__(
        self,
        credentials_json: Optional[str] = None,
        credentials_path: Optional[str] = None,
    ):
        self._token = _token(credentials_json, credentials_path)

    def _call(self, method: str, **params) -> dict:
        url = f"https://api.telegram.org/bot{self._token}/{method}"
        resp = requests.post(url, json=params or None, timeout=30)
        if resp.status_code >= 400:
            raise TelegramError(
                f"Telegram HTTP {resp.status_code}: {resp.text[:300]}",
                retryable=resp.status_code >= 500,
            )
        data = resp.json()
        if not data.get("ok"):
            raise TelegramError(
                f"Telegram API: {data.get('description') or 'unknown'}",
                error_code="TELEGRAM_API_ERROR",
            )
        return data.get("result") or {}

    def send_message(self, chat_id: str, text: str) -> dict:
        return self._call("sendMessage", chat_id=chat_id, text=text)

    def get_updates(self, limit: int = 20, offset: Optional[int] = None) -> list:
        params: dict[str, Any] = {"limit": max(1, min(limit, 100)), "timeout": 0}
        if offset is not None:
            params["offset"] = offset
        result = self._call("getUpdates", **params)
        return result if isinstance(result, list) else []
