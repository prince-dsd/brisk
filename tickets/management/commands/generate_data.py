from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from tickets.models import Passenger, Ticket, Berth, TicketHistory
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
        berth_types = ['lower', 'side-lower', 'upper', 'side-upper']
        for berth_type in berth_types:
            Berth.objects.create(berth_type=berth_type, availability_status='available')
        self.stdout.write(self.style.SUCCESS('Berths generated'))

    def generate_passengers(self):
        # Create a few passengers (100 for example)
        for _ in range(100):
            name = self.fake.name()
            age = random.randint(1, 80)
            is_child = age < 5
            Passenger.objects.create(name=name, age=age, is_child=is_child)
        self.stdout.write(self.style.SUCCESS('Passengers generated'))

    def generate_tickets(self):
        # Generate tickets for passengers
        ticket_types = ['confirmed', 'RAC', 'waiting-list']
        status_options = ['booked', 'canceled']

        for _ in range(100):  # Let's generate 100 tickets for example
            passenger = random.choice(Passenger.objects.all())
            ticket_type = random.choice(ticket_types)

            # Get an available berth
            available_berths = Berth.objects.filter(availability_status='available')
            if available_berths.exists():
                berth = random.choice(available_berths)
                berth.availability_status = 'booked'
                berth.save()

                ticket = Ticket.objects.create(
                    ticket_type=ticket_type,
                    status=random.choice(status_options),
                    passenger=passenger,
                    berth_allocation=berth.berth_type
                )

                self.stdout.write(f"Ticket generated for Passenger: {passenger.name} | Ticket Type: {ticket_type} | Berth: {berth.berth_type}")
        self.stdout.write(self.style.SUCCESS('Tickets generated'))

    def generate_ticket_history(self):
        # Generate some ticket history
        for ticket in Ticket.objects.all():
            actions = ['booked', 'canceled', 'promoted_from_RAC', 'moved_to_RAC']
            action = random.choice(actions)
            TicketHistory.objects.create(
                ticket=ticket,
                action=action,
                timestamp=self.fake.date_this_decade()
            )
        self.stdout.write(self.style.SUCCESS('Ticket history generated'))
