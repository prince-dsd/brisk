from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .error_handlers import handle_service_error, handle_ticket_error
from .serializers import TicketSerializer
from .services import (
    AvailabilityService,
    BookingService,
    cancel_ticket,
    get_booked_tickets,
)
from .swagger_schemas import (
    book_ticket_schema,
    cancel_ticket_schema,
    get_available_berths_schema,
    get_booked_tickets_schema,
)


class BaseTicketView(APIView):
    """Base view class with common functionality."""

    def create_response(self, data, status_code=status.HTTP_200_OK):
        return Response(data, status=status_code)


class BookTicketView(BaseTicketView):
    @swagger_auto_schema(**book_ticket_schema)
    def post(self, request):
        """Book tickets for multiple passengers."""
        try:
            booking_result = BookingService.process_booking_request(request.data.get("passengers", []))
            data, status_code = BookingService.format_booking_response(booking_result)
            return self.create_response(data, status_code)
        except Exception as e:
            return handle_service_error(e)


class CancelTicketView(BaseTicketView):
    @swagger_auto_schema(**cancel_ticket_schema)
    def post(self, request, ticket_id):
        """Cancel a specific ticket."""
        try:
            ticket, error = cancel_ticket(ticket_id)
            if error:
                return self.create_response({"error": error}, status.HTTP_400_BAD_REQUEST)
            return self.create_response({"message": "Ticket canceled successfully."})
        except Exception as e:
            return handle_service_error(e)


class GetBookedTicketsView(BaseTicketView):
    @swagger_auto_schema(**get_booked_tickets_schema)
    def get(self, request):
        """Get all booked tickets."""
        try:
            tickets = get_booked_tickets()
            return self.create_response(TicketSerializer(tickets, many=True).data)
        except Exception as e:
            return handle_service_error(e)


class GetAvailableTicketsView(BaseTicketView):
    @swagger_auto_schema(**get_available_berths_schema)
    def get(self, request):
        """Get available tickets and quota information."""
        try:
            return self.create_response(AvailabilityService.get_availability_info())
        except Exception as e:
            return handle_service_error(e)
