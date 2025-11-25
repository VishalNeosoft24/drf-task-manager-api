import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied


class ApiResponse:
    @staticmethod
    def success(
        data=None,
        message="Request processed successfully.",
        status_code=status.HTTP_200_OK,
    ):
        return Response(
            {
                "status": "success",
                "message": message,
                "data": data if data is not None else {},
            },
            status=status_code,
        )

    @staticmethod
    def error(
        errors=None,
        message="An unexpected error occurred.",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        return Response(
            {
                "status": "error",
                "message": message,
                "errors": errors if errors is not None else {},
            },
            status=status_code,
        )

    @staticmethod
    def serializer_error(
        serializer_errors,
        message="Invalid data provided.",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        formatted_errors = {
            field: error[0] if isinstance(error, list) else error
            for field, error in serializer_errors.items()
        }
        return Response(
            {"status": "error", "message": message, "errors": formatted_errors},
            status=status_code,
        )


def custom_exception_handler(exc, context):
    # Use the default DRF exception handler first
    response = exception_handler(exc, context)

    if isinstance(exc, PermissionDenied):
        # Handle PermissionDenied error and return a custom response
        return ApiResponse.error(
            message=str(exc), status_code=status.HTTP_403_FORBIDDEN
        )

    # Return the default response for other exceptions
    return response