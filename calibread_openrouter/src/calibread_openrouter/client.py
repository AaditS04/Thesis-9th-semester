"""Minimal OpenRouter HTTP client with deterministic request metadata and retries."""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .config import api_key


class OpenRouterClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        api = config["api"]
        self.base_url = str(api.get("base_url", "https://openrouter.ai/api/v1")).rstrip("/")
        self.timeout = float(api.get("timeout_seconds", 120))
        self.max_retries = int(api.get("max_retries", 5))
        self.retry_base = float(api.get("retry_base_seconds", 1.5))
        rpm = float(api.get("requests_per_minute", 0))
        self.minimum_interval = 60.0 / rpm if rpm > 0 else 0.0
        self.last_request_at = 0.0
        self.headers = {
            "Authorization": f"Bearer {api_key(config)}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api.get("http_referer"):
            self.headers["HTTP-Referer"] = str(api["http_referer"])
        if api.get("app_title"):
            self.headers["X-OpenRouter-Title"] = str(api["app_title"])

    def _throttle(self) -> None:
        remaining = self.minimum_interval - (time.monotonic() - self.last_request_at)
        if remaining > 0:
            time.sleep(remaining)

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_error: Dict[str, Any] = {}
        for attempt in range(self.max_retries + 1):
            self._throttle()
            started = time.monotonic()
            request = urllib.request.Request(url, data=body, headers=self.headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                self.last_request_at = time.monotonic()
                data["_attempt_count"] = attempt + 1
                data["_latency_ms"] = round((time.monotonic() - started) * 1000, 3)
                data["_received_at_utc"] = datetime.now(timezone.utc).isoformat()
                return data
            except urllib.error.HTTPError as exc:
                self.last_request_at = time.monotonic()
                raw = exc.read().decode("utf-8", errors="replace")
                try:
                    detail = json.loads(raw)
                except json.JSONDecodeError:
                    detail = {"raw": raw}
                last_error = {
                    "status": exc.code,
                    "message": _error_message(detail) or str(exc),
                    "detail": detail,
                    "attempt_count": attempt + 1,
                }
                retryable = exc.code in {408, 409, 425, 429} or exc.code >= 500
                if not retryable or attempt >= self.max_retries:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                self.last_request_at = time.monotonic()
                last_error = {
                    "status": 0,
                    "message": str(exc),
                    "detail": {},
                    "attempt_count": attempt + 1,
                }
                if attempt >= self.max_retries:
                    break
            delay = self.retry_base * (2**attempt) + random.Random(attempt).random() * 0.25
            time.sleep(delay)
        raise OpenRouterError(last_error)

    def list_models(self) -> List[Dict[str, Any]]:
        return list(self._request("GET", "models").get("data", []))

    def selected_model(self) -> Dict[str, Any]:
        selected = self.config["model"]["id"]
        for item in self.list_models():
            if item.get("id") == selected or item.get("canonical_slug") == selected:
                return item
        raise OpenRouterError({"status": 404, "message": f"Model not found: {selected}", "detail": {}})

    def chat(
        self,
        messages: List[Dict[str, str]],
        schema: Dict[str, Any],
        temperature: float,
        top_p: float,
        max_completion_tokens: int,
        seed: int,
        model_override: str = "",
        request_logprobs: Optional[bool] = None,
    ) -> Dict[str, Any]:
        generation = self.config["generation"]
        structured = bool(generation.get("structured_outputs", True))
        logprobs = bool(generation.get("request_logprobs", True)) if request_logprobs is None else request_logprobs
        payload: Dict[str, Any] = {
            "model": model_override or self.config["model"]["id"],
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_completion_tokens": max_completion_tokens,
            "seed": seed,
            "stream": False,
            "provider": _provider_payload(self.config["model"].get("provider", {})),
        }
        if structured:
            payload["response_format"] = {"type": "json_schema", "json_schema": schema}
        else:
            payload["response_format"] = {"type": "json_object"}
        if logprobs:
            payload["logprobs"] = True
            top = int(generation.get("top_logprobs", 0))
            if top > 0:
                payload["top_logprobs"] = top
        result = self._request("POST", "chat/completions", payload)
        return normalize_completion(result)


class OpenRouterError(RuntimeError):
    def __init__(self, detail: Dict[str, Any]):
        super().__init__(detail.get("message", "OpenRouter request failed"))
        self.detail = detail


def _provider_payload(provider: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key in (
        "only", "order", "allow_fallbacks", "require_parameters", "data_collection",
        "zdr", "sort", "ignore", "quantizations",
    ):
        value = provider.get(key)
        if value not in (None, [], ""):
            result[key] = value
    return result


def _error_message(detail: Dict[str, Any]) -> str:
    error = detail.get("error", detail)
    if isinstance(error, dict):
        return str(error.get("message", ""))
    return str(error) if error else ""


def normalize_completion(response: Dict[str, Any]) -> Dict[str, Any]:
    choices = response.get("choices") or []
    if not choices:
        raise OpenRouterError({
            "status": 502,
            "message": "OpenRouter response contained no choices",
            "detail": response,
            "attempt_count": response.get("_attempt_count", 1),
        })
    choice = choices[0]
    message = choice.get("message") or {}
    content = message.get("content", "")
    if isinstance(content, list):
        content = "".join(
            str(item.get("text", "")) if isinstance(item, dict) else str(item)
            for item in content
        )
    usage = response.get("usage") or {}
    return {
        "request_id": response.get("id", ""),
        "model_returned": response.get("model", ""),
        "provider_returned": response.get("provider", ""),
        "system_fingerprint": response.get("system_fingerprint", ""),
        "content": str(content),
        "logprobs": choice.get("logprobs"),
        "finish_reason": choice.get("finish_reason", ""),
        "native_finish_reason": choice.get("native_finish_reason", ""),
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
        "cost_credits": usage.get("cost", 0),
        "latency_ms": response.get("_latency_ms", 0),
        "created_at_utc": response.get("_received_at_utc", ""),
        "attempt_count": response.get("_attempt_count", 1),
        "raw_response": response,
    }
