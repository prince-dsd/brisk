from .models import Ticket, TicketHistory, Passenger, Berth
from django.core.exceptions import ValidationError

def cancel_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return None, "Ticket not found."

    if ticket.status == 'canceled':
        return None, "This ticket is already canceled."

    ticket.status = 'canceled'
    ticket.save()

    handle_promotions(ticket)

    # Create cancellation history
    TicketHistory.objects.create(ticket=ticket, action='canceled')

    return ticket, None

def handle_promotions(ticket):
    if ticket.ticket_type == 'confirmed':
        promote_next_rac_ticket()

    promote_next_waiting_list_ticket()

def promote_next_rac_ticket():
    next_rac_ticket = Ticket.objects.filter(ticket_type='RAC', status='booked').first()
    if next_rac_ticket:
        next_rac_ticket.ticket_type = 'confirmed'
        next_rac_ticket.save()
        TicketHistory.objects.create(ticket=next_rac_ticket, action='promoted_from_RAC')

def promote_next_waiting_list_ticket():
    waiting_list_ticket = Ticket.objects.filter(ticket_type='waiting-list', status='booked').first()
    if waiting_list_ticket:
        waiting_list_ticket.ticket_type = 'RAC'
        waiting_list_ticket.save()
        TicketHistory.objects.create(ticket=waiting_list_ticket, action='moved_to_RAC')

def book_ticket(passenger_name, passenger_age, ticket_type):
    if not passenger_name or not passenger_age or not ticket_type:
        return None, "All fields are required."

    passenger = Passenger.objects.create(name=passenger_name, age=passenger_age, is_child=(passenger_age < 5))

    try:
        # Use custom manager to check constraints
        Ticket.objects.check_confirmed_berths_limit()
        Ticket.objects.check_rac_limit()
        Ticket.objects.check_waiting_list_limit()

        # Assign berth based on priority
        berth = Ticket.objects.assign_berth_based_on_priority(passenger)
        if not berth:
            return None, "No available berths for this ticket."

        ticket = Ticket.objects.create(ticket_type=ticket_type, status='booked', passenger=passenger, berth_allocation=berth.berth_type)

        berth.availability_status = 'booked'
        berth.save()

        return ticket, None

    except ValidationError as e:
        return None, str(e)

def get_booked_tickets():
    return Ticket.objects.filter(status='booked')

def get_available_berths():
    return Berth.objects.filter(availability_status='available')