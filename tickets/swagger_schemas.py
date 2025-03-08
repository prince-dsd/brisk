from drf_yasg import openapi

from .serializers import BerthSerializer, TicketSerializer

cancel_ticket_schema = {
    "operation_description": "Cancels the ticket and handles the promotion logic.",
    "manual_parameters": [
        openapi.Parameter(
            "ticket_id",
            openapi.IN_PATH,
            description="ID of the ticket to cancel",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
    "responses": {
        200: openapi.Response(
            description="Ticket canceled successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={"message": openapi.Schema(type=openapi.TYPE_STRING)}
            ),
        ),
        400: openapi.Response(
            description="Bad request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={"error": openapi.Schema(type=openapi.TYPE_STRING)}
            ),
        ),
        404: openapi.Response(
            description="Ticket not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT, properties={"error": openapi.Schema(type=openapi.TYPE_STRING)}
            ),
        ),
    },
}

book_ticket_schema = {
    "operation_description": "Books tickets for multiple passengers.",
    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["passengers"],
        properties={
            "passengers": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    required=["name", "age"],
                    properties={
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "age": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "gender": openapi.Schema(type=openapi.TYPE_STRING, enum=["M", "F"]),
                        "has_child": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                    },
                ),
            ),
        },
    ),
    "responses": {
        201: openapi.Response(
            description="Tickets booked successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "booked_tickets": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "passenger_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "age": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "ticket_type": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    ),
                    "errors": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "passenger": openapi.Schema(type=openapi.TYPE_OBJECT),
                                "error": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="Bad request or validation errors",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "booked_tickets": openapi.Schema(
                        type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    ),
                    "errors": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                },
            ),
        ),
    },
}

get_booked_tickets_schema = {
    "operation_description": "Fetches a list of all booked tickets (i.e., confirmed and RAC tickets).",
    "responses": {
        200: openapi.Response(
            description="List of booked tickets",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "passenger_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "age": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "ticket_type": openapi.Schema(type=openapi.TYPE_STRING),
                        "status": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        )
    },
}

get_available_berths_schema = {
    "operation_description": "Fetches available berths and count information.",
    "responses": {
        200: openapi.Response(
            description="Available berths information",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "available_berths": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "berth_type": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    ),
                    "available_berths_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "quotas": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "confirmed_limit": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "rac_limit": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "waiting_list_limit": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                },
            ),
        )
    },
}
