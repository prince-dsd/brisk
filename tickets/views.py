from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket, Passenger, Berth, TicketHistory
from .serializers import TicketSerializer, PassengerSerializer, BerthSerializer, TicketHistorySerializer


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
    def post(self, request, ticket_id):
        """
        Cancels the ticket and handles the promotion logic.
        When a confirmed ticket is canceled, the next RAC ticket (if any) should become confirmed.
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

        if ticket.status == 'canceled':
            return Response({"message": "This ticket is already canceled."}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = 'canceled'
        ticket.save()

        # Handle promotions (RAC → Confirmed, Waiting-list → RAC)
        if ticket.ticket_type == 'confirmed':
            # Find the next RAC ticket to promote to confirmed
            next_rac_ticket = Ticket.objects.filter(ticket_type='RAC', status='booked').first()
            if next_rac_ticket:
                next_rac_ticket.ticket_type = 'confirmed'
                next_rac_ticket.save()
                TicketHistory.objects.create(ticket=next_rac_ticket, action='promoted_from_RAC')

        # Handle waiting-list promotion
        waiting_list_ticket = Ticket.objects.filter(ticket_type='waiting-list', status='booked').first()
        if waiting_list_ticket:
            waiting_list_ticket.ticket_type = 'RAC'
            waiting_list_ticket.save()
            TicketHistory.objects.create(ticket=waiting_list_ticket, action='moved_to_RAC')

        # Create cancellation history
        TicketHistory.objects.create(ticket=ticket, action='canceled')

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
