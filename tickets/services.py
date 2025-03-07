from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import OperationalError
from rest_framework import status
from .serializers import TicketSerializer, BerthSerializer

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
    """Book a ticket with concurrency handling"""
    if not _validate_booking_params(passenger_name, passenger_age):
        return None, REQUIRED_FIELDS

    try:
        passenger = _create_passenger(passenger_name, passenger_age, gender)
        ticket_details = _determine_ticket_type_and_berth(passenger, has_child)
        
        if "error" in ticket_details:
            return None, ticket_details["error"]
            
        ticket = _create_ticket(passenger, ticket_details)
        return ticket, None

    except OperationalError:
        return None, "Booking temporarily unavailable. Please try again."
    except ValidationError as e:
        return None, str(e)

def _validate_booking_params(name, age):
    """Validate basic booking parameters."""
    return bool(name and age is not None)

def _create_passenger(name, age, gender):
    """Create a new passenger record."""
    is_child = age < CHILD_AGE
    return Passenger.objects.create(
        name=name,
        age=age,
        is_child=is_child,
        gender=gender
    )

@transaction.atomic
def _determine_ticket_type_and_berth(passenger, has_child):
    """Determine ticket type and berth allocation based on availability."""
    ticket_counts = _get_current_ticket_counts()
    
    # Determine ticket type
    ticket_type = _get_available_ticket_type(ticket_counts)
    if not ticket_type:
        return {"error": NO_TICKETS_AVAILABLE}

    # Handle berth allocation
    berth = None
    if not passenger.is_child:
        berth = _allocate_berth(ticket_type, passenger.age, passenger.gender, has_child)
        if not berth and ticket_type != WAITING_LIST:
            return {"error": NO_BERTH_AVAILABLE}

    return {
        "ticket_type": ticket_type,
        "berth": berth
    }

def _get_current_ticket_counts():
    """Get current counts of different ticket types with locking."""
    return {
        "confirmed": Ticket.objects.select_for_update(nowait=True)
                    .filter(ticket_type=CONFIRMED, status=BOOKED).count(),
        "rac": Ticket.objects.select_for_update(nowait=True)
                    .filter(ticket_type=RAC, status=BOOKED).count(),
        "waiting": Ticket.objects.select_for_update(nowait=True)
                    .filter(ticket_type=WAITING_LIST, status=BOOKED).count()
    }

def _get_available_ticket_type(counts):
    """Determine available ticket type based on current counts."""
    if counts["confirmed"] < CONFIRMED_BERTH_LIMIT:
        return CONFIRMED
    if counts["rac"] < RAC_TICKET_LIMIT:
        return RAC
    if counts["waiting"] < WAITING_LIST_LIMIT:
        return WAITING_LIST
    return None

def _allocate_berth(ticket_type, age, gender, has_child):
    """Allocate appropriate berth based on ticket type and passenger details."""
    if ticket_type == CONFIRMED:
        return _allocate_confirmed_berth_with_lock(age, gender, has_child)
    elif ticket_type == RAC:
        return _allocate_rac_berth_with_lock()
    return None

def _create_ticket(passenger, ticket_details):
    """Create ticket and update berth status."""
    ticket = Ticket.objects.create(
        ticket_type=ticket_details["ticket_type"],
        status=BOOKED,
        passenger=passenger,
        berth_allocation=ticket_details["berth"].berth_type if ticket_details["berth"] else None,
    )

    if ticket_details["berth"]:
        ticket_details["berth"].availability_status = BOOKED
        ticket_details["berth"].save()

    return ticket


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


class BookingService:
    """Service class for handling passenger booking operations."""
    
    REQUIRED_FIELDS = ["name", "age"]
    
    @classmethod
    def process_booking_request(cls, passengers_data):
        """Process multiple passenger booking requests."""
        if not passengers_data:
            return cls._create_error_response("No passengers provided")

        booking_results = cls._process_passenger_bookings(passengers_data)
        return cls._create_booking_response(booking_results)

    @classmethod
    def _process_passenger_bookings(cls, passengers_data):
        """Process bookings for multiple passengers."""
        booked_tickets = []
        errors = []

        for passenger_data in passengers_data:
            booking_result = cls._process_single_booking(passenger_data)
            if booking_result.get("error"):
                errors.append(booking_result)
            else:
                booked_tickets.append(booking_result["ticket"])

        return {"booked_tickets": booked_tickets, "errors": errors}

    @classmethod
    def _process_single_booking(cls, passenger_data):
        """Process booking for a single passenger."""
        if not cls._validate_passenger_data(passenger_data):
            return {
                "error": "Missing required fields",
                "passenger": passenger_data
            }

        ticket, error = book_ticket(
            passenger_name=passenger_data.get("name"),
            passenger_age=passenger_data.get("age"),
            gender=passenger_data.get("gender"),
            has_child=passenger_data.get("has_child", False),
            parent_id=passenger_data.get("parent_id")
        )

        return {"ticket": ticket} if ticket else {
            "error": error,
            "passenger": passenger_data
        }

    @classmethod
    def _validate_passenger_data(cls, passenger_data):
        """Validate required passenger booking data."""
        return all(passenger_data.get(field) for field in cls.REQUIRED_FIELDS)

    @staticmethod
    def _create_error_response(message):
        """Create a standardized error response."""
        return {
            "error": message,
            "status_code": status.HTTP_400_BAD_REQUEST
        }

    @staticmethod
    def _create_booking_response(booking_results):
        """Create a standardized booking response."""
        return {
            "booked_tickets": booking_results["booked_tickets"],
            "errors": booking_results["errors"],
            "status_code": (
                status.HTTP_201_CREATED 
                if booking_results["booked_tickets"] 
                else status.HTTP_400_BAD_REQUEST
            )
        }

    @staticmethod
    def format_booking_response(booking_result):
        """Format the booking response data for API."""
        if "error" in booking_result:
            return {"error": booking_result["error"]}, booking_result["status_code"]
            
        return {
            "booked_tickets": TicketSerializer(booking_result["booked_tickets"], many=True).data,
            "errors": booking_result["errors"]
        }, booking_result["status_code"]


class AvailabilityService:
    @staticmethod
    def get_availability_info():
        """Get system-wide availability information."""
        available_berths = get_available_berths()
        return {
            "available_berths": BerthSerializer(available_berths, many=True).data,
            "available_berths_count": available_berths.count(),
            "quotas": {
                "confirmed_limit": CONFIRMED_BERTH_LIMIT,
                "rac_limit": RAC_TICKET_LIMIT,
                "waiting_list_limit": WAITING_LIST_LIMIT,
            }
        }
