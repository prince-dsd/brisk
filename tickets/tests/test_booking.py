from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase, override_settings

from ..constants import (
    AVAILABLE, BOOKED, CONFIRMED, GENDER_FEMALE, LOWER,
    NO_CONFIRMED_BERTHS, NO_RAC_BERTHS, NO_TICKETS_AVAILABLE,
    RAC, SIDE_LOWER, SIDE_UPPER, UPPER, WAITING_LIST,
    NO_BERTH_AVAILABLE, ACTION_CANCELED
)
from ..models import Berth, Passenger, Ticket
from ..services import book_ticket, cancel_ticket


@override_settings(DATABASE={'atomic_requests': True})
class TicketBookingTest(TestCase):
    """Test cases for ticket booking system."""
    
    use_transaction_fixtures = True

    @classmethod
    def setUpClass(cls):
        """Create berth data once for all test methods."""
        super().setUpClass()
        with transaction.atomic():
            cls._create_initial_berths()

    @classmethod
    def _create_initial_berths(cls):
        """Create the initial berth distribution if not exists."""
        if not Berth.objects.exists():
            berth_distribution = {
                LOWER: 18,      # 9 compartments × 2 lower berths
                UPPER: 18,      # 9 compartments × 2 upper berths
                SIDE_LOWER: 18, # 9 compartments × 2 middle berths
                SIDE_UPPER: 18  # 9 side upper berths
            }
            
            berths_to_create = []
            for berth_type, count in berth_distribution.items():
                berths_to_create.extend([
                    Berth(
                        berth_type=berth_type,
                        availability_status=AVAILABLE
                    ) for _ in range(count)
                ])
            
            Berth.objects.bulk_create(berths_to_create)
            print(f"\nCreated {len(berths_to_create)} berths:")
            for berth_type, count in berth_distribution.items():
                print(f" - {berth_type}: {count}")

    def setUp(self):
        """Reset data before each test."""
        super().setUp()
        # Reset all berth statuses to available
        Berth.objects.all().update(availability_status=AVAILABLE)
        
        # Verify berth distribution
        berth_counts = {
            berth_type: Berth.objects.filter(berth_type=berth_type).count()
            for berth_type in [LOWER, UPPER, SIDE_LOWER, SIDE_UPPER]
        }
        total_berths = sum(berth_counts.values())
        
        if total_berths != 72:
            raise ValueError(f"Expected 72 berths, found {total_berths}")

    def tearDown(self):
        """Clean up after each test."""
        super().tearDown()
        # Clean only tickets and passengers, preserve berths
        Ticket.objects.all().delete()
        Passenger.objects.all().delete()

    def test_confirmed_berth_limit(self):
        """Test that system cannot book more than 63 confirmed tickets."""
        # Book 63 confirmed tickets
        booked_tickets = 0
        for i in range(63):
            ticket, error = book_ticket(f"Passenger{i}", 30, CONFIRMED)
            if error:
                self.fail(f"Failed to book ticket {i}: {error}")
            booked_tickets += 1

        # Try to book one more confirmed ticket
        ticket, error = book_ticket("ExtraPassenger", 30, CONFIRMED)
        self.assertIsNone(ticket, "Should not create ticket beyond limit")
        self.assertEqual(error, NO_CONFIRMED_BERTHS)

    def test_rac_limit(self):
        """Test that system cannot book more than 18 RAC tickets."""
        # Book all confirmed tickets first
        for i in range(63):
            book_ticket(f"Passenger{i}", 30, CONFIRMED)

        # Book 18 RAC tickets
        for i in range(18):
            ticket, error = book_ticket(f"RACPassenger{i}", 30, RAC)
            self.assertIsNone(error)
            self.assertIsNotNone(ticket)

        # Try to book one more RAC ticket
        ticket, error = book_ticket("ExtraRAC", 30, RAC)
        self.assertIsNone(ticket)
        self.assertEqual(error, NO_RAC_BERTHS)

    def test_waiting_list_limit(self):
        """Test that system cannot book more than 10 waiting-list tickets."""
        # Book all confirmed and RAC tickets first
        for i in range(63):
            book_ticket(f"Passenger{i}", 30, CONFIRMED)
        for i in range(18):
            book_ticket(f"RACPassenger{i}", 30, RAC)

        # Book 10 waiting-list tickets
        for i in range(10):
            ticket, error = book_ticket(f"WLPassenger{i}", 30, WAITING_LIST)
            self.assertIsNone(error)
            self.assertIsNotNone(ticket)

        # Try to book one more waiting-list ticket
        ticket, error = book_ticket("ExtraWL", 30, WAITING_LIST)
        self.assertIsNone(ticket)
        self.assertEqual(error, NO_TICKETS_AVAILABLE)

    def test_child_under_five(self):
        """Test that children under 5 are stored but don't get berth."""
        ticket, error = book_ticket("Child", 4, CONFIRMED)
        self.assertIsNone(error)
        self.assertIsNotNone(ticket)
        self.assertIsNone(ticket.berth_allocation)
        self.assertTrue(ticket.passenger.is_child)

    def test_senior_citizen_priority(self):
        """Test that passengers aged 60+ get priority for lower berths."""
        senior_ticket, error = book_ticket("Senior", 65, CONFIRMED)
        self.assertIsNone(error)
        self.assertEqual(senior_ticket.berth_allocation, LOWER)

    def test_lady_with_child_priority(self):
        """Test that ladies with children get priority for lower berths."""
        lady_ticket, error = book_ticket(
            "Lady", 30, CONFIRMED,
            gender=GENDER_FEMALE, has_child=True
        )
        self.assertIsNone(error)
        self.assertEqual(lady_ticket.berth_allocation, LOWER)

    def test_rac_side_lower_allocation(self):
        """Test that RAC passengers are allocated side-lower berths."""
        rac_ticket, error = book_ticket("RACPassenger", 30, RAC)
        self.assertIsNone(error)
        self.assertEqual(rac_ticket.berth_allocation, SIDE_LOWER)

    def test_promotion_on_cancellation(self):
        """Test that RAC/WL tickets are promoted when confirmed ticket is cancelled."""
        # Book confirmed, RAC and WL tickets
        conf_ticket, _ = book_ticket("Confirmed", 30, CONFIRMED)
        rac_ticket, _ = book_ticket("RAC", 30, RAC)
        wl_ticket, _ = book_ticket("WL", 30, WAITING_LIST)

        # Cancel confirmed ticket
        cancel_ticket(conf_ticket.id)

        # Check if RAC ticket was promoted to confirmed
        updated_rac = Ticket.objects.get(id=rac_ticket.id)
        self.assertEqual(updated_rac.ticket_type, CONFIRMED)

        # Check if WL ticket was promoted to RAC
        updated_wl = Ticket.objects.get(id=wl_ticket.id)
        self.assertEqual(updated_wl.ticket_type, RAC)

    def test_berth_preference_distribution(self):
        """Test that berths are distributed evenly when no special preferences."""
        berth_counts = {LOWER: 0, UPPER: 0, SIDE_LOWER: 0, SIDE_UPPER: 0}
        
        # Book 10 tickets for regular passengers
        for i in range(10):
            ticket, error = book_ticket(f"Passenger{i}", 30, CONFIRMED)
            self.assertIsNone(error)
            berth_counts[ticket.berth_allocation] += 1
        
        # Check if distribution is relatively even
        self.assertTrue(all(count > 0 for count in berth_counts.values()))

    def test_consecutive_cancellations(self):
        """Test multiple consecutive cancellations and promotions."""
        # Book tickets in different categories
        conf_tickets = []
        for i in range(3):
            ticket, _ = book_ticket(f"Confirmed{i}", 30, CONFIRMED)
            conf_tickets.append(ticket)
        
        rac_tickets = []
        for i in range(2):
            ticket, _ = book_ticket(f"RAC{i}", 30, RAC)
            rac_tickets.append(ticket)
        
        wl_tickets = []
        for i in range(2):
            ticket, _ = book_ticket(f"WL{i}", 30, WAITING_LIST)
            wl_tickets.append(ticket)

        # Cancel confirmed tickets one by one
        for conf_ticket in conf_tickets:
            cancel_ticket(conf_ticket.id)
            # Verify RAC promotion
            updated_rac = Ticket.objects.get(id=rac_tickets[0].id)
            self.assertEqual(updated_rac.ticket_type, CONFIRMED)
            # Verify WL promotion
            updated_wl = Ticket.objects.get(id=wl_tickets[0].id)
            self.assertEqual(updated_wl.ticket_type, RAC)

    def test_cancel_nonexistent_ticket(self):
        """Test cancellation of non-existent ticket."""
        result, error = cancel_ticket(999999)
        self.assertIsNone(result)
        self.assertEqual(error, TICKET_NOT_FOUND)

    def test_double_cancellation(self):
        """Test attempting to cancel the same ticket twice."""
        ticket, _ = book_ticket("TestPassenger", 30, CONFIRMED)
        
        # First cancellation
        result1, error1 = cancel_ticket(ticket.id)
        self.assertIsNone(error1)
        
        # Second cancellation
        result2, error2 = cancel_ticket(ticket.id)
        self.assertIsNone(result2)
        self.assertEqual(error2, ALREADY_CANCELED)

    def test_booking_validation(self):
        """Test validation of booking parameters."""
        # Test missing name
        ticket, error = book_ticket("", 30, CONFIRMED)
        self.assertIsNone(ticket)
        self.assertEqual(error, REQUIRED_FIELDS)
        
        # Test invalid age
        ticket, error = book_ticket("Test", -1, CONFIRMED)
        self.assertIsNone(ticket)

    def test_berth_availability_tracking(self):
        """Test that berth availability is correctly tracked."""
        initial_available = Berth.objects.filter(availability_status=AVAILABLE).count()
        
        # Book a confirmed ticket
        ticket, _ = book_ticket("Test", 30, CONFIRMED)
        
        # Check berth status
        new_available = Berth.objects.filter(availability_status=AVAILABLE).count()
        self.assertEqual(new_available, initial_available - 1)
        
        # Cancel ticket
        cancel_ticket(ticket.id)
        
        # Check berth status is restored
        final_available = Berth.objects.filter(availability_status=AVAILABLE).count()
        self.assertEqual(final_available, initial_available)

    def test_ticket_history_tracking(self):
        """Test that ticket history is properly recorded."""
        # Book a ticket
        ticket, _ = book_ticket("HistoryTest", 30, CONFIRMED)
        
        # Check initial history
        history = TicketHistory.objects.filter(ticket=ticket)
        self.assertTrue(history.exists())
        
        # Cancel ticket
        cancel_ticket(ticket.id)
        
        # Check cancellation history
        history = TicketHistory.objects.filter(ticket=ticket)
        self.assertEqual(history.count(), 2)  # Booking + Cancellation
        self.assertEqual(history.last().action, ACTION_CANCELED)
