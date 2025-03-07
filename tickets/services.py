from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import OperationalError

from .constants import (ACTION_CANCELED, ACTION_MOVED_RAC, ACTION_PROMOTED_RAC, ALREADY_CANCELED, AVAILABLE, BOOKED,
                        CANCELED, CHILD_AGE, CONFIRMED, GENDER_FEMALE, LOWER, NO_BERTH_AVAILABLE, NO_CONFIRMED_BERTHS,
                        NO_RAC_BERTHS, NO_TICKETS_AVAILABLE, RAC, REQUIRED_FIELDS, SENIOR_AGE, SIDE_LOWER,
                        TICKET_NOT_FOUND, WAITING_LIST)
from .models import Berth, Passenger, Ticket, TicketHistory

CONFIRMED_BERTH_LIMIT = 63
RAC_TICKET_LIMIT = 18
WAITING_LIST_LIMIT = 10


@transaction.atomic
def book_ticket(passenger_name, passenger_age, gender=None, has_child=False):
    """
    Book a ticket with concurrency handling
    """
    if not passenger_name or not passenger_age:
        return None, REQUIRED_FIELDS

    try:
        # Create passenger first
        is_child = passenger_age < CHILD_AGE
        passenger = Passenger.objects.create(name=passenger_name, age=passenger_age, is_child=is_child, gender=gender)

        # Lock the ticket counts for atomic operations
        with transaction.atomic():
            # Get current counts with locks
            confirmed_count = Ticket.objects.select_for_update(nowait=True).filter(
                ticket_type=CONFIRMED, status=BOOKED
            ).count()
            rac_count = Ticket.objects.select_for_update(nowait=True).filter(
                ticket_type=RAC, status=BOOKED
            ).count()
            waiting_count = Ticket.objects.select_for_update(nowait=True).filter(
                ticket_type=WAITING_LIST, status=BOOKED
            ).count()

            # Determine ticket type
            if confirmed_count < CONFIRMED_BERTH_LIMIT:
                ticket_type = CONFIRMED
            elif rac_count < RAC_TICKET_LIMIT:
                ticket_type = RAC
            elif waiting_count < WAITING_LIST_LIMIT:
                ticket_type = WAITING_LIST
            else:
                return None, NO_TICKETS_AVAILABLE

            # Handle berth allocation with locking
            berth = None
            if not is_child:
                if ticket_type == CONFIRMED:
                    berth = _allocate_confirmed_berth_with_lock(passenger_age, gender, has_child)
                elif ticket_type == RAC:
                    berth = _allocate_rac_berth_with_lock()

            if not berth and ticket_type != WAITING_LIST:
                return None, NO_BERTH_AVAILABLE

            # Create ticket
            ticket = Ticket.objects.create(
                ticket_type=ticket_type,
                status=BOOKED,
                passenger=passenger,
                berth_allocation=berth.berth_type if berth else None,
            )

            # Update berth status if allocated
            if berth:
                berth.availability_status = BOOKED
                berth.save()

            return ticket, None

    except OperationalError:
        # Handle deadlock or lock wait timeout
        return None, "Booking temporarily unavailable. Please try again."
    except ValidationError as e:
        return None, str(e)


def _allocate_confirmed_berth_with_lock(age, gender, has_child):
    """
    Allocate berth with proper locking
    """
    available_berths = Berth.objects.select_for_update(nowait=True).filter(
        availability_status=AVAILABLE
    )

    if age >= SENIOR_AGE or (gender == GENDER_FEMALE and has_child):
        lower_berth = available_berths.filter(berth_type=LOWER).first()
        if lower_berth:
            return lower_berth

    return available_berths.exclude(berth_type=SIDE_LOWER).first()


def _allocate_rac_berth_with_lock():
    """
    Allocate RAC berth with proper locking
    """
    return Berth.objects.select_for_update(nowait=True).filter(
        berth_type=SIDE_LOWER, 
        availability_status=AVAILABLE
    ).first()


def cancel_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return None, TICKET_NOT_FOUND

    if ticket.status == CANCELED:
        return None, ALREADY_CANCELED

    ticket.status = CANCELED
    ticket.save()

    handle_promotions(ticket)

    # Create cancellation history
    TicketHistory.objects.create(ticket=ticket, action=ACTION_CANCELED)

    return ticket, None


def handle_promotions(ticket):
    if ticket.ticket_type == CONFIRMED:
        promote_next_rac_ticket()

    promote_next_waiting_list_ticket()


def promote_next_rac_ticket():
    next_rac_ticket = Ticket.objects.filter(ticket_type=RAC, status=BOOKED).first()
    if next_rac_ticket:
        next_rac_ticket.ticket_type = CONFIRMED
        next_rac_ticket.save()
        TicketHistory.objects.create(ticket=next_rac_ticket, action=ACTION_PROMOTED_RAC)


def promote_next_waiting_list_ticket():
    waiting_list_ticket = Ticket.objects.filter(ticket_type=WAITING_LIST, status=BOOKED).first()
    if waiting_list_ticket:
        waiting_list_ticket.ticket_type = RAC
        waiting_list_ticket.save()
        TicketHistory.objects.create(ticket=waiting_list_ticket, action=ACTION_MOVED_RAC)


def get_booked_tickets():
    return Ticket.objects.filter(status=BOOKED)


def get_available_berths():
    return Berth.objects.filter(availability_status=AVAILABLE)
