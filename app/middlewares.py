import redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

redis_blocked_ip = redis.Redis(host='localhost', port=6379, db=0)
redis_attempts = redis.Redis(host='localhost', port=6379, db=1)


class FailedRequestLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if redis_blocked_ip.get(request.client.host):
            return Response("You are blocked because of too many requests", status_code=429)

        # process the request and get the response
        response = await call_next(request)
        if not response.status_code == 302:
            return response

        if response.headers.get('err') in ('Password not passed', 'No user with such email', 'Captcha not solved', 'OTP code not correct'):
            failed_attempts = redis_attempts.get(request.client.host)
            if failed_attempts and int(failed_attempts) > 4:
                redis_blocked_ip.set(request.client.host, 'T')
                redis_blocked_ip.expire(request.client.host, 600)
                redis_attempts.set(request.client.host, 0)
            else:
                redis_attempts.incrby(request.client.host, 1)
        return response
