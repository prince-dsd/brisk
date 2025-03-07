from django.db import transaction
from .models import Ticket, TicketHistory, Passenger, Berth
from django.core.exceptions import ValidationError

CONFIRMED_BERTH_LIMIT = 63
RAC_TICKET_LIMIT = 18
WAITING_LIST_LIMIT = 10

@transaction.atomic
def book_ticket(passenger_name, passenger_age, ticket_type, gender=None, has_child=False):
    """
    Book a ticket with the given constraints and priorities
    """
    if not passenger_name or not passenger_age or not ticket_type:
        return None, "All fields are required."

    # Create passenger first
    is_child = passenger_age < 5
    passenger = Passenger.objects.create(
        name=passenger_name,
        age=passenger_age,
        is_child=is_child,
        gender=gender
    )

    try:
        # Check booking limits based on ticket type
        if ticket_type == 'confirmed':
            if Ticket.objects.filter(ticket_type='confirmed', status='booked').count() >= CONFIRMED_BERTH_LIMIT:
                return None, "No confirmed berths available"
        elif ticket_type == 'RAC':
            if Ticket.objects.filter(ticket_type='RAC', status='booked').count() >= RAC_TICKET_LIMIT:
                return None, "No RAC berths available"
        elif ticket_type == 'waiting-list':
            if Ticket.objects.filter(ticket_type='waiting-list', status='booked').count() >= WAITING_LIST_LIMIT:
                return None, "No tickets available"

        # Handle berth allocation
        berth = None
        if not is_child:  # Children under 5 don't get berth
            if ticket_type == 'confirmed':
                berth = _allocate_confirmed_berth(passenger_age, gender, has_child)
            elif ticket_type == 'RAC':
                berth = _allocate_rac_berth()

        if not berth and ticket_type != 'waiting-list':
            return None, "No available berths for this ticket."

        # Create ticket
        ticket = Ticket.objects.create(
            ticket_type=ticket_type,
            status='booked',
            passenger=passenger,
            berth_allocation=berth.berth_type if berth else None
        )

        # Update berth status if allocated
        if berth:
            berth.availability_status = 'booked'
            berth.save()

        return ticket, None

    except ValidationError as e:
        return None, str(e)

def _allocate_confirmed_berth(age, gender, has_child):
    """
    Allocate berth based on priority:
    1. Seniors (60+) get lower berth
    2. Ladies with children get lower berth
    3. Others get any available berth
    """
    available_berths = Berth.objects.filter(availability_status='available')
    
    # Priority allocation for lower berths
    if age >= 60 or (gender == 'F' and has_child):
        lower_berth = available_berths.filter(berth_type='lower').first()
        if lower_berth:
            return lower_berth

    # Regular allocation for others
    return available_berths.exclude(berth_type='side-lower').first()

def _allocate_rac_berth():
    """
    Allocate side-lower berth for RAC passengers
    """
    return Berth.objects.filter(
        berth_type='side-lower',
        availability_status='available'
    ).first()

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

def get_booked_tickets():
    return Ticket.objects.filter(status='booked')

def get_available_berths():
    return Berth.objects.filter(availability_status='available')