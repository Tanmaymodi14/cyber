#!/usr/bin/env python3
"""
Lambda entrypoint wrapping FastAPI via Mangum with defensive event normalization.

Why: Some API Gateway/Invoke variants omit requestContext.http.sourceIp.
Mangum <handler> expects it and raises KeyError. We normalize the event to
include a default sourceIp so the app always runs.
"""

from __future__ import annotations

from mangum import Mangum
from api_server import app


# Mangum ASGI adapter
_asgi_handler = Mangum(app)


def handler(event, context):
    """Lambda handler with robust event normalization for API Gateway v2."""
    try:
        if isinstance(event, dict):
            request_context = event.get("requestContext") or {}
            http_ctx = request_context.get("http") or {}
            # Ensure sourceIp exists to prevent Mangum KeyError
            if "sourceIp" not in http_ctx:
                identity = request_context.get("identity") or {}
                http_ctx["sourceIp"] = identity.get("sourceIp", "0.0.0.0")
                request_context["http"] = http_ctx
                event["requestContext"] = request_context
        print("lambda_function.handler: normalized event keys:", list(event.keys()) if isinstance(event, dict) else type(event))
        rc = event.get("requestContext", {}) if isinstance(event, dict) else {}
        hc = rc.get("http", {})
        print("lambda_function.handler: http ctx:", {k: hc.get(k) for k in ["method", "path", "sourceIp"]})
    except Exception:
        # Never block the request due to normalization issues
        pass

    return _asgi_handler(event, context)


