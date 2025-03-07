from datetime import datetime

import random

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from tickets.constants import AVAILABILITY_STATUS, BERTH_TYPES, HISTORY_ACTIONS, TICKET_STATUS, TICKET_TYPES
from tickets.models import Berth, Passenger, Ticket, TicketHistory


class Command(BaseCommand):
    help = "Generates artificial data for the railway ticket reservation system"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Generate Berths
                self.generate_berths()

                # Generate Passengers
                # self.generate_passengers()

                # Generate Tickets
                # self.generate_tickets()

                # Generate Ticket History
                # self.generate_ticket_history()

            self.stdout.write(self.style.SUCCESS("Successfully generated artificial data"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))

    def generate_berths(self):
        """Generate 72 berths with realistic distribution."""
        # Distribution of berths in a typical coach
        berth_distribution = {
            "lower": 18,  # 9 compartments × 2 lower berths
            "middle": 18,  # 9 compartments × 2 middle berths
            "upper": 18,  # 9 compartments × 2 upper berths
            "side_lower": 9,  # 9 side lower berths
            "side_upper": 9,  # 9 side upper berths
        }

        coach_number = "S1"  # Sample coach number
        berth_counter = 1

        for berth_type, count in berth_distribution.items():
            for _ in range(count):
                Berth.objects.create(
                    berth_type=berth_type,
                    availability_status=AVAILABILITY_STATUS[0][0],  # 'available'
                    berth_number=berth_counter,
                )
                berth_counter += 1

        total_berths = sum(berth_distribution.values())
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {total_berths} berths in coach {coach_number}\n"
                f'Distribution: {", ".join(f"{k}: {v}" for k, v in berth_distribution.items())}'
            )
        )

    def generate_passengers(self):
        for _ in range(100):
            name = self.fake.name()
            age = random.randint(1, 80)
            gender = random.choice(["M", "F"])  # Match model choices
            # is_child will be set automatically by model save() method
            Passenger.objects.create(name=name, age=age, gender=gender)
        self.stdout.write(self.style.SUCCESS("Generated 100 passengers"))

    def generate_tickets(self):
        # Use constants instead of hardcoded values
        ticket_types = [t[0] for t in TICKET_TYPES]
        status_options = [s[0] for s in TICKET_STATUS]

        for _ in range(100):
            passenger = random.choice(Passenger.objects.all())
            ticket_type = random.choice(ticket_types)

            # Get an available berth
            available_berths = Berth.objects.filter(availability_status=AVAILABILITY_STATUS[0][0])  # 'available'

            if available_berths.exists():
                berth = random.choice(available_berths)
                berth.availability_status = AVAILABILITY_STATUS[1][0]  # 'booked'
                berth.save()

                ticket = Ticket.objects.create(
                    ticket_type=ticket_type,
                    status=random.choice(status_options),
                    passenger=passenger,
                    berth_allocation=berth.berth_type,
                )

                self.stdout.write(
                    f"Ticket generated for Passenger: {passenger.name} | "
                    f"Ticket Type: {ticket_type} | "
                    f"Berth: {berth.berth_type}"
                )

        self.stdout.write(self.style.SUCCESS("Tickets generated"))

    def generate_ticket_history(self):
        # Use HISTORY_ACTIONS from constants
        actions = [action[0] for action in HISTORY_ACTIONS]

        for ticket in Ticket.objects.all():
            # Create 1-3 history entries per ticket
            for _ in range(random.randint(1, 3)):
                TicketHistory.objects.create(
                    ticket=ticket,
                    action=random.choice(actions),
                    # timestamp will be set automatically by auto_now_add
                )

        self.stdout.write(self.style.SUCCESS("Ticket history generated"))
