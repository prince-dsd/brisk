from drf_yasg import openapi

cancel_ticket_schema = {
    'operation_description': "Cancels the ticket and handles the promotion logic.",
    'manual_parameters': [
        openapi.Parameter(
            'ticket_id',
            openapi.IN_PATH,
            description="ID of the ticket to cancel",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    'responses': {
        200: openapi.Response(
            description="Ticket canceled successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(
            description="Bad request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        404: openapi.Response(
            description="Ticket not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
}

book_ticket_schema = {
    'operation_description': "Books a ticket for a passenger.",
    'request_body': openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'age', 'ticket_type'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the passenger'),
            'age': openapi.Schema(type=openapi.TYPE_INTEGER, description='Age of the passenger'),
            'ticket_type': openapi.Schema(type=openapi.TYPE_STRING, description='Type of the ticket', enum=['confirmed', 'RAC', 'waiting-list']),
        }
    ),
    'responses': {
        201: openapi.Response(
            description="Ticket booked successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'ticket_type': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'passenger': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'age': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'is_child': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }
                    ),
                    'berth_allocation': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                }
            )
        ),
        400: openapi.Response(
            description="Bad request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
}

# Add more schemas for other views here