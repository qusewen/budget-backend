from fastapi import Request, Response
from app.database.database import AsyncSessionLocal, AuditLog
from typing import Optional, Dict, Any

from app.helpers.auth.check_login import get_current_user


async def log_audit(
        request: Request,
        response: Response,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
):
    async with AsyncSessionLocal() as db:
        try:
            try:
                user = await get_current_user(request, response, db)
                current_user_id = str(user.id) if user and hasattr(user, 'id') else None
            except Exception as e:
                print(f"⚠️ Could not get user: {e}")
                current_user_id = None

            final_user_id = user_id or current_user_id or "anonymous"

            ip = request.client.host if request.client else "unknown"
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()

            log_entry = AuditLog(
                user_id=str(final_user_id)[:100],
                action=action,
                resource=resource,
                resource_id=str(resource_id)[:100] if resource_id else None,
                details=details or {},
                ip_address=ip,
                user_agent=request.headers.get("user-agent", "unknown")[:500]
            )

            db.add(log_entry)
            await db.commit()

        except Exception as e:
            print(f"❌ Audit error: {e}")
            await db.rollback()