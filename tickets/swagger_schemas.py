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

# Add more schemas for other views here