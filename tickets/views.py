from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import TicketSerializer, BerthSerializer
from .services import (book_ticket, cancel_ticket, get_booked_tickets, 
                      get_available_berths, CONFIRMED_BERTH_LIMIT, 
                      RAC_TICKET_LIMIT, WAITING_LIST_LIMIT)
from .swagger_schemas import (book_ticket_schema, cancel_ticket_schema, 
                            get_booked_tickets_schema, get_available_berths_schema)
from .error_handlers import handle_ticket_error, handle_service_error, handle_validation_error

class BookTicketView(APIView):
    @swagger_auto_schema(**book_ticket_schema)
    def post(self, request):
        passenger_name = request.data.get('name')
        passenger_age = request.data.get('age')
        ticket_type = request.data.get('ticket_type')
        gender = request.data.get('gender')
        has_child = request.data.get('has_child', False)

        if not all([passenger_name, passenger_age, ticket_type]):
            return handle_validation_error(['name', 'age', 'ticket_type'])

        try:
            ticket, error = book_ticket(
                passenger_name=passenger_name,
                passenger_age=passenger_age,
                ticket_type=ticket_type,
                gender=gender,
                has_child=has_child
            )
            if error:
                return handle_ticket_error(error)

            return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return handle_service_error(e)

class CancelTicketView(APIView):
    @swagger_auto_schema(**cancel_ticket_schema)
    def post(self, request, ticket_id):
        try:
            ticket, error = cancel_ticket(ticket_id)
            if error:
                return handle_ticket_error(error)

            return Response({"message": "Ticket canceled successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_service_error(e)

class GetBookedTicketsView(APIView):
    @swagger_auto_schema(**get_booked_tickets_schema)
    def get(self, request):
        try:
            tickets = get_booked_tickets()
            return Response(TicketSerializer(tickets, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_service_error(e)

class GetAvailableTicketsView(APIView):
    @swagger_auto_schema(**get_available_berths_schema)
    def get(self, request):
        try:
            available_berths = get_available_berths()
            return Response({
                "available_berths": BerthSerializer(available_berths, many=True).data,
                "quotas": {
                    "confirmed_limit": CONFIRMED_BERTH_LIMIT,
                    "rac_limit": RAC_TICKET_LIMIT,
                    "waiting_list_limit": WAITING_LIST_LIMIT
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_service_error(e)
