import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from server.app.exceptions import LawyerGPTError

logger = logging.getLogger("lawyergpt.exceptions")


async def lawyergpt_exception_handler(request: Request, exc: LawyerGPTError) -> JSONResponse:
    logger.error("LawyerGPTError: %s [%s] path=%s", exc.message, exc.error_code, request.url.path)
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s: %s", request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred", "error_code": "INTERNAL_ERROR"},
    )
