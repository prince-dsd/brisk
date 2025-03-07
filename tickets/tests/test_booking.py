from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Berth, Passenger, Ticket
from ..services import book_ticket, cancel_ticket


class TicketBookingTest(TestCase):
    def setUp(self):
        # Create berths
        berth_types = ["lower"] * 54 + ["upper"] * 54 + ["side-lower"] * 9 + ["side-upper"] * 9
        for berth_type in berth_types:
            Berth.objects.create(berth_type=berth_type, availability_status="available")

    def test_confirmed_berth_limit(self):
        """Test that system cannot book more than 63 confirmed tickets"""
        # Book 63 confirmed tickets
        for i in range(63):
            ticket, error = book_ticket(f"Passenger{i}", 30, "confirmed")
            self.assertIsNone(error)

        # Try to book one more confirmed ticket
        ticket, error = book_ticket("ExtraPassenger", 30, "confirmed")
        self.assertEqual(error, "No confirmed berths available")

    def test_rac_limit(self):
        """Test that system cannot book more than 18 RAC tickets"""
        # Book all confirmed tickets first
        for i in range(63):
            book_ticket(f"Passenger{i}", 30, "confirmed")

        # Book 18 RAC tickets
        for i in range(18):
            ticket, error = book_ticket(f"RACPassenger{i}", 30, "RAC")
            self.assertIsNone(error)

        # Try to book one more RAC ticket
        ticket, error = book_ticket("ExtraRAC", 30, "RAC")
        self.assertEqual(error, "No RAC berths available")

    def test_waiting_list_limit(self):
        """Test that system cannot book more than 10 waiting-list tickets"""
        # Book all confirmed and RAC tickets first
        for i in range(63):
            book_ticket(f"Passenger{i}", 30, "confirmed")
        for i in range(18):
            book_ticket(f"RACPassenger{i}", 30, "RAC")

        # Book 10 waiting-list tickets
        for i in range(10):
            ticket, error = book_ticket(f"WLPassenger{i}", 30, "waiting-list")
            self.assertIsNone(error)

        # Try to book one more waiting-list ticket
        ticket, error = book_ticket("ExtraWL", 30, "waiting-list")
        self.assertEqual(error, "No tickets available")

    def test_child_under_five(self):
        """Test that children under 5 are stored but don't get berth"""
        ticket, error = book_ticket("Child", 4, "confirmed")
        self.assertIsNone(error)
        self.assertIsNotNone(ticket)
        self.assertIsNone(ticket.berth_allocation)
        self.assertTrue(ticket.passenger.is_child)

    def test_senior_citizen_priority(self):
        """Test that passengers aged 60+ get priority for lower berths"""
        # Book a ticket for senior citizen
        senior_ticket, error = book_ticket("Senior", 65, "confirmed")
        self.assertIsNone(error)
        self.assertEqual(senior_ticket.berth_allocation, "lower")

    def test_lady_with_child_priority(self):
        """Test that ladies with children get priority for lower berths"""
        # Book a ticket for lady with child
        lady_ticket, error = book_ticket("Lady", 30, "confirmed", has_child=True, gender="F")
        self.assertIsNone(error)
        self.assertEqual(lady_ticket.berth_allocation, "lower")

    def test_rac_side_lower_allocation(self):
        """Test that RAC passengers are allocated side-lower berths"""
        # Book a RAC ticket
        rac_ticket, error = book_ticket("RACPassenger", 30, "RAC")
        self.assertIsNone(error)
        self.assertEqual(rac_ticket.berth_allocation, "side-lower")

    def test_promotion_on_cancellation(self):
        """Test that RAC/WL tickets are promoted when confirmed ticket is cancelled"""
        # Book confirmed, RAC and WL tickets
        conf_ticket, _ = book_ticket("Confirmed", 30, "confirmed")
        rac_ticket, _ = book_ticket("RAC", 30, "RAC")
        wl_ticket, _ = book_ticket("WL", 30, "waiting-list")

        # Cancel confirmed ticket
        cancel_ticket(conf_ticket.id)

        # Check if RAC ticket was promoted to confirmed
        updated_rac = Ticket.objects.get(id=rac_ticket.id)
        self.assertEqual(updated_rac.ticket_type, "confirmed")

        # Check if WL ticket was promoted to RAC
        updated_wl = Ticket.objects.get(id=wl_ticket.id)
        self.assertEqual(updated_wl.ticket_type, "RAC")
