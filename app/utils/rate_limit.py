import time
from collections import defaultdict
from threading import Lock
from flask import request, jsonify

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = Lock()
        self.window = 60
        self.max_requests = 5

    def _get_identifier(self):
        return request.remote_addr or 'unknown'

    def is_allowed(self, identifier=None):
        if identifier is None:
            identifier = self._get_identifier()

        current_time = time.time()

        with self.lock:
            if identifier not in self.requests:
                self.requests[identifier] = []

            self.requests[identifier] = [
                t for t in self.requests[identifier]
                if current_time - t < self.window
            ]

            if len(self.requests[identifier]) >= self.max_requests:
                return False, self._get_remaining_time(identifier)

            self.requests[identifier].append(current_time)
            return True, 0

    def _get_remaining_time(self, identifier):
        if identifier not in self.requests or not self.requests[identifier]:
            return 0
        oldest = min(self.requests[identifier])
        elapsed = time.time() - oldest
        return int(self.window - elapsed)

    def get_remaining(self, identifier=None):
        if identifier is None:
            identifier = self._get_identifier()

        current_time = time.time()

        with self.lock:
            if identifier not in self.requests:
                return self.max_requests

            self.requests[identifier] = [
                t for t in self.requests[identifier]
                if current_time - t < self.window
            ]

            return max(0, self.max_requests - len(self.requests[identifier]))


rate_limiter = RateLimiter()


def check_rate_limit(identifier=None):
    allowed, remaining_time = rate_limiter.is_allowed(identifier)
    if not allowed:
        return False, remaining_time
    return True, 0


def get_rate_limit_info():
    identifier = request.remote_addr or 'unknown'
    remaining = rate_limiter.get_remaining(identifier)
    return {
        'remaining': remaining,
        'limit': rate_limiter.max_requests,
        'window': rate_limiter.window
    }