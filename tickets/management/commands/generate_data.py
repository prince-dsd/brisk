from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from tickets.models import Passenger, Ticket, Berth, TicketHistory
from tickets.constants import TICKET_TYPES, TICKET_STATUS, BERTH_TYPES, AVAILABILITY_STATUS, HISTORY_ACTIONS
import random
from datetime import datetime

class Command(BaseCommand):
    help = 'Generates artificial data for the railway ticket reservation system'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()
    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                # Generate Berths
                self.generate_berths()

                # Generate Passengers
                self.generate_passengers()

                # Generate Tickets
                self.generate_tickets()

                # Generate Ticket History
                self.generate_ticket_history()

            self.stdout.write(self.style.SUCCESS('Successfully generated artificial data'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

    def generate_berths(self):
        # Use BERTH_TYPES from constants instead of hardcoding
        for berth_type, _ in BERTH_TYPES:
            for _ in range(10):  # Create multiple berths of each type
                Berth.objects.create(
                    berth_type=berth_type,
                    availability_status=AVAILABILITY_STATUS[0][0]  # 'available'
                )
        self.stdout.write(self.style.SUCCESS(f'Berths generated for types: {", ".join(dict(BERTH_TYPES).keys())}'))

    def generate_passengers(self):
        for _ in range(100):
            name = self.fake.name()
            age = random.randint(1, 80)
            gender = random.choice(['M', 'F'])  # Match model choices
            # is_child will be set automatically by model save() method
            Passenger.objects.create(
                name=name,
                age=age,
                gender=gender
            )
        self.stdout.write(self.style.SUCCESS('Generated 100 passengers'))

    def generate_tickets(self):
        # Use constants instead of hardcoded values
        ticket_types = [t[0] for t in TICKET_TYPES]
        status_options = [s[0] for s in TICKET_STATUS]

        for _ in range(100):
            passenger = random.choice(Passenger.objects.all())
            ticket_type = random.choice(ticket_types)

            # Get an available berth
            available_berths = Berth.objects.filter(
                availability_status=AVAILABILITY_STATUS[0][0]  # 'available'
            )
            
            if available_berths.exists():
                berth = random.choice(available_berths)
                berth.availability_status = AVAILABILITY_STATUS[1][0]  # 'booked'
                berth.save()

                ticket = Ticket.objects.create(
                    ticket_type=ticket_type,
                    status=random.choice(status_options),
                    passenger=passenger,
                    berth_allocation=berth.berth_type
                )

                self.stdout.write(
                    f"Ticket generated for Passenger: {passenger.name} | "
                    f"Ticket Type: {ticket_type} | "
                    f"Berth: {berth.berth_type}"
                )
        
        self.stdout.write(self.style.SUCCESS('Tickets generated'))

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
                
        self.stdout.write(self.style.SUCCESS('Ticket history generated'))
