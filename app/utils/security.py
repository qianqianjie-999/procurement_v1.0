import time
from collections import defaultdict
from threading import Lock
from flask import request

class LoginRateLimiter:
    def __init__(self, max_attempts=5, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = defaultdict(list)
        self.lock = Lock()

    def _get_identifier(self):
        return request.remote_addr or 'unknown'

    def record_failed_login(self):
        ip = self._get_identifier()
        current_time = time.time()
        with self.lock:
            self.attempts[ip] = [
                t for t in self.attempts[ip]
                if current_time - t < self.window_seconds
            ]
            self.attempts[ip].append(current_time)

    def is_locked_out(self):
        ip = self._get_identifier()
        current_time = time.time()
        with self.lock:
            if ip not in self.attempts:
                return False, 0

            self.attempts[ip] = [
                t for t in self.attempts[ip]
                if current_time - t < self.window_seconds
            ]

            if len(self.attempts[ip]) >= self.max_attempts:
                oldest = min(self.attempts[ip])
                remaining = int(self.window_seconds - (current_time - oldest))
                return True, max(0, remaining)

            return False, 0

    def reset_attempts(self):
        ip = self._get_identifier()
        with self.lock:
            if ip in self.attempts:
                del self.attempts[ip]

    def get_remaining_attempts(self):
        ip = self._get_identifier()
        current_time = time.time()
        with self.lock:
            if ip not in self.attempts:
                return self.max_attempts

            self.attempts[ip] = [
                t for t in self.attempts[ip]
                if current_time - t < self.window_seconds
            ]

            return max(0, self.max_attempts - len(self.attempts[ip]))


login_rate_limiter = LoginRateLimiter(max_attempts=5, window_seconds=300)
