from django.db import models
from .managers import TicketManager

class Passenger(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    is_child = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}, Age: {self.age}"

class Ticket(models.Model):
    TICKET_TYPES = [
        ('confirmed', 'Confirmed'),
        ('RAC', 'RAC'),
        ('waiting-list', 'Waiting List')
    ]

    TICKET_STATUS = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled')
    ]

    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    status = models.CharField(max_length=20, choices=TICKET_STATUS, default='booked')
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    berth_allocation = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Attach the custom manager
    objects = TicketManager()

    def __str__(self):
        return f"Ticket for {self.passenger.name} - {self.ticket_type} - {self.status}"

class Berth(models.Model):
    BERTH_TYPES = [
        ('lower', 'Lower'),
        ('side-lower', 'Side-Lower'),
        ('upper', 'Upper'),
        ('side-upper', 'Side-Upper')
    ]

    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('reserved', 'Reserved')
    ]

    berth_type = models.CharField(max_length=20, choices=BERTH_TYPES)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='available')

    def __str__(self):
        return f"{self.berth_type} - {self.availability_status}"

class TicketHistory(models.Model):
    ACTIONS = [
        ('booked', 'Booked'),
        ('canceled', 'Canceled'),
        ('moved_to_RAC', 'Moved to RAC'),
        ('promoted_from_waiting', 'Promoted from Waiting List'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket ID: {self.ticket.id} - Action: {self.action} - {self.timestamp}"
