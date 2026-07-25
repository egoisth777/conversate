"""Receiver adapters for the fidelity harness.

A receiver hands a context pack to a fresh session and returns its answer to a
scripted continuation task. Credentials are read from the environment only; nothing
about them is stored in a result. When a provider is not configured or its transport
never answers, the cell is `unevaluated` - never a pass, never a scored miss.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 0.0


def redact(text: str, secrets: list[str]) -> str:
    for secret in secrets:
        if secret:
            text = text.replace(secret, "<redacted>")
    return text


@dataclass
class Receiver:
    name: str
    provider: str
    model: str
    host: str
    credential_env: str
    available: bool
    reason: str = ""
    transport: object | None = None
    _secrets: list[str] = field(default_factory=list, repr=False)

    def describe(self) -> dict:
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self.model,
            "host": self.host,
            "credential_env": self.credential_env,
            "available": self.available,
            "reason": self.reason,
        }

    def run(self, *, pack_text: str, task: str) -> dict:
        if not self.available or self.transport is None:
            return self._unevaluated(self.reason or "no credential configured")

        request = {
            "provider": self.provider,
            "model": self.model,
            "host": self.host,
            "context": pack_text,
            "task": task,
        }
        retries = 0
        last_error = ""
        started = time.perf_counter()
        for attempt in range(MAX_ATTEMPTS):
            try:
                response = self.transport(request)
            except Exception as error:  # transport faults are evidence, not crashes
                retries = attempt + 1
                last_error = redact(f"{type(error).__name__}: {error}", self._secrets)
                if RETRY_DELAY_SECONDS:
                    time.sleep(RETRY_DELAY_SECONDS)
                continue
            latency_ms = (time.perf_counter() - started) * 1000
            return {
                "receiver": self.name,
                "status": "evaluated",
                "answer": redact(str(response.get("answer", "")), self._secrets),
                "passed": True,
                "reason": "",
                "telemetry": {
                    "provider": self.provider,
                    "model": self.model,
                    "host": self.host,
                    "input_tokens": response.get("input_tokens"),
                    "output_tokens": response.get("output_tokens"),
                    "retries": retries,
                    "intervention": bool(response.get("intervention", False)),
                    "latency_ms": latency_ms,
                },
            }
        return self._unevaluated(
            f"transport did not answer after {MAX_ATTEMPTS} attempts: {last_error}",
            retries=retries,
        )

    def _unevaluated(self, reason: str, retries: int = 0) -> dict:
        return {
            "receiver": self.name,
            "status": "unevaluated",
            "answer": None,
            "passed": False,
            "reason": redact(reason, self._secrets),
            "telemetry": {
                "provider": self.provider,
                "model": self.model,
                "host": self.host,
                "input_tokens": None,
                "output_tokens": None,
                "retries": retries,
                "intervention": False,
                "latency_ms": None,
            },
        }


def load_receivers(config: dict, env: dict, transport=None) -> list[Receiver]:
    """Build one receiver per configured provider; missing credentials stay visible."""
    receivers: list[Receiver] = []
    for entry in config.get("receivers", []):
        credential_env = entry.get("credential_env", "")
        secret = env.get(credential_env, "")
        available = bool(secret) and transport is not None
        if not secret:
            reason = f"no credential in environment variable {credential_env}"
        elif transport is None:
            reason = "no transport configured for this run"
        else:
            reason = ""
        receivers.append(
            Receiver(
                name=entry.get("name", entry.get("provider", "unnamed")),
                provider=entry.get("provider", "unknown"),
                model=entry.get("model", "unknown"),
                host=entry.get("host", "unknown"),
                credential_env=credential_env,
                available=available,
                reason=reason,
                transport=transport,
                _secrets=[secret] if secret else [],
            )
        )
    return receivers


def run_with_baseline(receiver: Receiver, *, pack_text: str, raw_text: str, task: str) -> dict:
    """Run the scripted task twice: once on the pack, once on the raw record."""
    return {
        "pack": receiver.run(pack_text=pack_text, task=task),
        "raw_baseline": receiver.run(pack_text=raw_text, task=task),
    }
