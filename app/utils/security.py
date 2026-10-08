"""登录失败限流（服务端、账号级、跨进程共享）。

2026-10-07 重写。原实现以 request.remote_addr 为键，而本架构下 frp 为 L4 透传，
服务端看到的源地址恒为内网 frpc 地址（实测 192.168.31.75）⇒
  ① 全局单桶：任一人失败 5 次即锁住全公司（DoS）；
  ② 成功登录 reset_attempts() 清空整桶 ⇒ 攻击者用自己注册的账号登录一次即清零，
     撞库限流实际不存在。
现改为按【账号】计数：只锁被攻击的账号，成功登录只清当前账号。
对外接口保持向后兼容（方法名不变，新增 username 参数）。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from login_guard import LoginGuard

_DB = os.environ.get('LOGIN_GUARD_DB', '/var/lib/login_guard/procurement.db')


class LoginRateLimiter(object):
    """薄适配层：保留原有方法名，限流键由 IP 改为账号（username）。"""

    def __init__(self, max_attempts=5, window_seconds=300, db_path=None, name='procurement'):
        self.max_attempts = int(max_attempts)
        self.window_seconds = int(window_seconds)
        self._guard = LoginGuard(db_path or _DB, max_fails=self.max_attempts,
                                 window=self.window_seconds, name=name)

    def record_failed_login(self, username):
        self._guard.record_failure(username)

    def is_locked_out(self, username):
        return self._guard.is_locked(username)

    def get_remaining_attempts(self, username):
        return self._guard.remaining_attempts(username)

    def reset_attempts(self, username):
        self._guard.reset(username)

    def global_pressure(self):
        return self._guard.global_pressure()


login_rate_limiter = LoginRateLimiter(max_attempts=5, window_seconds=300)
