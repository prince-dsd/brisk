from django.urls import path

from .views import BookTicketView, CancelTicketView, GetAvailableTicketsView, GetBookedTicketsView

urlpatterns = [
    # Endpoint to book a ticket
    path("api/v1/tickets/book", BookTicketView.as_view(), name="book_ticket"),
    # Endpoint to cancel a ticket
    path("api/v1/tickets/cancel/<int:ticket_id>", CancelTicketView.as_view(), name="cancel_ticket"),
    # Endpoint to get the list of booked tickets
    path("api/v1/tickets/booked", GetBookedTicketsView.as_view(), name="get_booked_tickets"),
    # Endpoint to get the list of available tickets (berths)
    path("api/v1/tickets/available", GetAvailableTicketsView.as_view(), name="get_available_tickets"),
]
