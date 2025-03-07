from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket, Passenger, Berth, TicketHistory
from .serializers import TicketSerializer, PassengerSerializer, BerthSerializer, TicketHistorySerializer
from drf_yasg.utils import swagger_auto_schema
from .swagger_schemas import cancel_ticket_schema, book_ticket_schema, get_booked_tickets_schema, get_available_berths_schema
from .services import cancel_ticket, book_ticket, get_booked_tickets, get_available_berths


# Book Ticket
class BookTicketView(APIView):
    @swagger_auto_schema(**book_ticket_schema)
    def post(self, request):
        passenger_name = request.data.get('name')
        passenger_age = request.data.get('age')
        ticket_type = request.data.get('ticket_type')

        ticket, error = book_ticket(passenger_name, passenger_age, ticket_type)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

# Cancel Ticket
class CancelTicketView(APIView):
    @swagger_auto_schema(**cancel_ticket_schema)
    def post(self, request, ticket_id):
        """
        Cancels the ticket and handles the promotion logic.
        When a confirmed ticket is canceled, the next RAC ticket (if any) should become confirmed.
        """
        ticket, error = cancel_ticket(ticket_id)
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST if error == "This ticket is already canceled." else status.HTTP_404_NOT_FOUND)

        return Response({"message": "Ticket canceled successfully."}, status=status.HTTP_200_OK)

# Get Booked Tickets
class GetBookedTicketsView(APIView):
    @swagger_auto_schema(**get_booked_tickets_schema)
    def get(self, request):
        """
        Fetches a list of all booked tickets (i.e., confirmed and RAC tickets).
        """
        tickets = get_booked_tickets()
        return Response(TicketSerializer(tickets, many=True).data, status=status.HTTP_200_OK)

# Get Available Tickets
class GetAvailableTicketsView(APIView):
    @swagger_auto_schema(**get_available_berths_schema)
    def get(self, request):
        """
        Fetches available berths.
        This can be used to show which tickets are available for booking.
        """
        available_berths = get_available_berths()
        available_berths_data = BerthSerializer(available_berths, many=True).data

        return Response({"available_berths": available_berths_data}, status=status.HTTP_200_OK)
