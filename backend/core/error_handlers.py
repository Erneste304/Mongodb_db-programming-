from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.core.exceptions import PermissionDenied, ApprovalRequired, ResourceNotFound


async def permission_denied_handler(request: Request, exc: PermissionDenied):
    """Handle permission denied exceptions"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)}
    )


async def approval_required_handler(request: Request, exc: ApprovalRequired):
    """Handle approval required exceptions"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc), "requires_approval": True}
    )


async def resource_not_found_handler(request: Request, exc: ResourceNotFound):
    """Handle resource not found exceptions"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "message": str(exc)}
    )
