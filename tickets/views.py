from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .error_handlers import handle_service_error, handle_ticket_error, handle_validation_error
from .serializers import BerthSerializer, TicketSerializer
from .services import (CONFIRMED_BERTH_LIMIT, RAC_TICKET_LIMIT, WAITING_LIST_LIMIT, book_ticket, cancel_ticket,
                       get_available_berths, get_booked_tickets)
from .swagger_schemas import (book_ticket_schema, cancel_ticket_schema, get_available_berths_schema,
                              get_booked_tickets_schema)


class BookTicketView(APIView):
    @swagger_auto_schema(**book_ticket_schema)
    def post(self, request):
        passengers = request.data.get("passengers", [])
        if not passengers:
            return handle_validation_error(["passengers"])

        try:
            booked_tickets = []
            errors = []

            for passenger in passengers:
                passenger_name = passenger.get("name")
                passenger_age = passenger.get("age")
                gender = passenger.get("gender")
                has_child = passenger.get("has_child", False)

                if not all([passenger_name, passenger_age]):
                    errors.append({
                        "passenger": passenger,
                        "error": "Missing required fields: name, age"
                    })
                    continue

                ticket, error = book_ticket(
                    passenger_name=passenger_name,
                    passenger_age=passenger_age,
                    gender=gender,
                    has_child=has_child,
                )

                if error:
                    errors.append({
                        "passenger": passenger,
                        "error": error
                    })
                else:
                    booked_tickets.append(ticket)

            response_data = {
                "booked_tickets": TicketSerializer(booked_tickets, many=True).data,
                "errors": errors
            }

            # Return 201 if at least one ticket was booked, otherwise 400
            status_code = status.HTTP_201_CREATED if booked_tickets else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=status_code)

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
            return Response(
                {
                    "available_berths": BerthSerializer(available_berths, many=True).data,
                    "quotas": {
                        "confirmed_limit": CONFIRMED_BERTH_LIMIT,
                        "rac_limit": RAC_TICKET_LIMIT,
                        "waiting_list_limit": WAITING_LIST_LIMIT,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return handle_service_error(e)
