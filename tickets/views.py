from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket, Passenger, Berth, TicketHistory
from .serializers import TicketSerializer, PassengerSerializer, BerthSerializer, TicketHistorySerializer
from drf_yasg.utils import swagger_auto_schema
from .swagger_schemas import cancel_ticket_schema
from .services import cancel_ticket


# Book Ticket
class BookTicketView(APIView):
    def post(self, request):
        passenger_name = request.data.get('name')
        passenger_age = request.data.get('age')
        ticket_type = request.data.get('ticket_type')

        if not passenger_name or not passenger_age or not ticket_type:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        passenger = Passenger.objects.create(name=passenger_name, age=passenger_age, is_child=(passenger_age < 5))

        try:
            # Use custom manager to check constraints
            Ticket.objects.check_confirmed_berths_limit()
            Ticket.objects.check_rac_limit()
            Ticket.objects.check_waiting_list_limit()

            # Assign berth based on priority
            berth = Ticket.objects.assign_berth_based_on_priority(passenger)
            if not berth:
                return Response({"error": "No available berths for this ticket."}, status=status.HTTP_400_BAD_REQUEST)

            ticket = Ticket.objects.create(ticket_type=ticket_type, status='booked', passenger=passenger, berth_allocation=berth.berth_type)

            berth.availability_status = 'booked'
            berth.save()

            return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    def get(self, request):
        """
        Fetches a list of all booked tickets (i.e., confirmed and RAC tickets).
        """
        tickets = Ticket.objects.filter(status='booked')
        return Response(TicketSerializer(tickets, many=True).data, status=status.HTTP_200_OK)

# Get Available Tickets
class GetAvailableTicketsView(APIView):
    def get(self, request):
        """
        Fetches available berths.
        This can be used to show which tickets are available for booking.
        """
        # Filtering available berths
        available_berths = Berth.objects.filter(availability_status='available')

        # Prepare response data
        available_berths_data = BerthSerializer(available_berths, many=True).data

        return Response({"available_berths": available_berths_data}, status=status.HTTP_200_OK)
