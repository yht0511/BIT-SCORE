"""Thread-safe bridge between bit_login's SMS callback and the Web UI."""

import re
import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional


class SmsChallengeError(Exception):
    """Raised when a Web SMS submission cannot be accepted."""


@dataclass
class _SmsChallenge:
    challenge_id: str
    masked_phone: str
    purpose: str
    created_at: float
    expires_at: float
    status: str = "waiting_sms"
    message: str = ""
    completed_at: Optional[float] = None
    code: Optional[str] = field(default=None, repr=False)
    ready: threading.Event = field(default_factory=threading.Event, repr=False)


class SmsVerificationBroker:
    """Pass one-time SMS codes from Flask requests to login worker threads."""

    _CODE_PATTERN = re.compile(r"^[0-9]{4,8}$")

    def __init__(self, timeout_seconds: int = 300, result_ttl: int = 4):
        self.timeout_seconds = timeout_seconds
        self.result_ttl = result_ttl
        self._lock = threading.Lock()
        self._challenges: Dict[str, _SmsChallenge] = {}
        self._thread_state = threading.local()

    def request_code(self, context) -> str:
        """Callback used by bit_login; blocks until the Web submits a code."""
        now = time.time()
        masked_phone = str(
            getattr(context, "masked_phone", "")
            or getattr(context, "phone", "")
            or "绑定手机"
        )
        challenge = _SmsChallenge(
            challenge_id=secrets.token_urlsafe(18),
            masked_phone=masked_phone,
            purpose=str(getattr(context, "purpose", "") or "password_second_factor"),
            created_at=now,
            expires_at=now + self.timeout_seconds,
        )

        with self._lock:
            self._cleanup_locked(now)
            self._challenges[challenge.challenge_id] = challenge
            self._thread_state.challenge_id = challenge.challenge_id

        print(
            f"短信验证码已发送至 {masked_phone}，请在 Web 页面完成验证。",
            flush=True,
        )

        if not challenge.ready.wait(self.timeout_seconds):
            with self._lock:
                challenge.status = "expired"
                challenge.message = "验证码已过期，程序将自动重新发起登录"
                challenge.completed_at = time.time()
            raise TimeoutError("等待 Web 页面提交短信验证码超时")

        with self._lock:
            code = challenge.code
            challenge.code = None
        if not code:
            raise SmsChallengeError("未收到有效的短信验证码")
        return code

    def submit(self, challenge_id: str, code: str) -> None:
        """Validate and deliver a code to the matching login worker."""
        challenge_id = str(challenge_id or "").strip()
        code = str(code or "").strip()
        if not challenge_id:
            raise SmsChallengeError("验证码请求不存在，请刷新页面后重试")
        if not self._CODE_PATTERN.fullmatch(code):
            raise SmsChallengeError("请输入 4 至 8 位数字验证码")

        now = time.time()
        with self._lock:
            self._cleanup_locked(now)
            challenge = self._challenges.get(challenge_id)
            if challenge is None:
                raise SmsChallengeError("验证码请求已失效，请等待系统重新发送")
            if now >= challenge.expires_at or challenge.status == "expired":
                raise SmsChallengeError("验证码已过期，请等待系统重新发送")
            if challenge.status != "waiting_sms":
                raise SmsChallengeError("验证码已提交，请勿重复操作")

            challenge.code = code
            challenge.status = "verifying"
            challenge.message = "验证码已提交，正在验证"
            challenge.ready.set()

    def finish_current(self, success: bool) -> None:
        """Mark the challenge used by the current login thread as complete."""
        challenge_id = getattr(self._thread_state, "challenge_id", None)
        if not challenge_id:
            return

        with self._lock:
            challenge = self._challenges.get(challenge_id)
            if challenge is not None and challenge.status != "expired":
                challenge.status = "succeeded" if success else "failed"
                challenge.message = (
                    "验证成功，登录正在继续"
                    if success
                    else "本次登录未完成，程序将自动重新发起登录"
                )
                challenge.completed_at = time.time()
        self._thread_state.challenge_id = None

    def snapshot(self) -> dict:
        """Return a safe, code-free view for the Web status endpoint."""
        now = time.time()
        with self._lock:
            self._cleanup_locked(now)
            challenges = list(self._challenges.values())
            if not challenges:
                return {"status": "idle"}

            # If another login is already waiting, let the user handle it before
            # showing short-lived success/failure feedback from an earlier one.
            priority = {
                "waiting_sms": 0,
                "verifying": 1,
                "failed": 2,
                "expired": 3,
                "succeeded": 4,
            }
            challenge = min(
                challenges,
                key=lambda item: (priority.get(item.status, 9), item.created_at),
            )
            return {
                "status": challenge.status,
                "challenge_id": challenge.challenge_id,
                "masked_phone": challenge.masked_phone,
                "purpose": challenge.purpose,
                "expires_in": max(0, int(challenge.expires_at - now)),
                "message": challenge.message,
            }

    def _cleanup_locked(self, now: float) -> None:
        for challenge in self._challenges.values():
            if challenge.status == "waiting_sms" and now >= challenge.expires_at:
                challenge.status = "expired"
                challenge.message = "验证码已过期，程序将自动重新发起登录"
                challenge.completed_at = now

        removable = [
            challenge_id
            for challenge_id, challenge in self._challenges.items()
            if challenge.completed_at is not None
            and now - challenge.completed_at >= self.result_ttl
        ]
        for challenge_id in removable:
            del self._challenges[challenge_id]


sms_broker = SmsVerificationBroker()
