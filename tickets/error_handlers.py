from rest_framework import status
from rest_framework.response import Response


def handle_ticket_error(error):
    """
    Handle common ticket booking and cancellation errors
    """
    if error == "Ticket not found.":
        return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)
    return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)


def handle_service_error(error):
    """
    Handle service-level errors and exceptions
    """
    return Response({"error": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_validation_error(fields=None):
    """
    Handle validation errors for required fields
    """
    message = "Required fields missing"
    if fields:
        message += f": {', '.join(fields)}"
    return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
