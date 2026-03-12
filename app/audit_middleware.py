from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import asyncio

from app.database.audit import log_audit


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await self._get_request_body(request)

        response = await call_next(request)

        if request.method in ["POST", "PUT", "PATCH", "DELETE", "GET"]:
            path_parts = request.url.path.strip("/").split("/")
            resource = path_parts[1] if len(path_parts) > 1 else path_parts[0] if path_parts else "unknown"

            details = {
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "status_code": response.status_code,
                "duration_ms": round((time.time() - start_time) * 1000, 2)
            }

            if body:
                details["request_body"] = body

            asyncio.create_task(
                log_audit(
                    request=request,
                    response=response,
                    action=request.method,
                    resource=resource,
                    details=details
                )
            )

        return response

    async def _get_request_body(self, request: Request):

        try:
            body_bytes = await request.body()

            async def receive():
                return {"type": "http.request", "body": body_bytes}

            request._receive = receive

            if body_bytes:
                try:
                    return json.loads(body_bytes)
                except:
                    body_str = body_bytes.decode('utf-8')[:500]
                    return {"raw_body": body_str}
            return None
        except Exception as e:
            print(f"⚠️ Error reading body: {e}")
            return None