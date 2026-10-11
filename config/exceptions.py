import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """DRF's default handling, plus clean JSON for DB integrity and unexpected errors."""
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "Database integrity error. The record may be a duplicate or still referenced."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    logger.exception("Unhandled error", exc_info=exc)
    return Response(
        {"detail": "Internal server error."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
