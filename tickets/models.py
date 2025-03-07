from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    AVAILABILITY_STATUS, BERTH_TYPES, CHILD_AGE, GENDER_CHOICES,
    HISTORY_ACTIONS, TICKET_STATUS, TICKET_TYPES
)
from .managers import TicketManager


class Passenger(models.Model):
    """Model representing a passenger in the ticket booking system."""

    name = models.CharField(max_length=255, help_text="Full name of the passenger")
    age = models.IntegerField(validators=[MinValueValidator(0)], help_text="Age of the passenger")
    is_child = models.BooleanField(default=False, help_text="Indicates if passenger is under 5 years old")
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        help_text="Gender of the passenger",
    )

    class Meta:
        verbose_name = "Passenger"
        verbose_name_plural = "Passengers"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, Age: {self.age}"

    def save(self, *args, **kwargs):
        """Override save to automatically set is_child based on age."""
        self.is_child = self.age < CHILD_AGE
        super().save(*args, **kwargs)


class Ticket(models.Model):
    """Model representing a ticket in the booking system."""

    ticket_type = models.CharField(
        max_length=20,
        choices=TICKET_TYPES,
        help_text="Type of ticket (Confirmed/RAC/Waiting List)"
    )
    status = models.CharField(
        max_length=20,
        choices=TICKET_STATUS,
        default=TICKET_STATUS[0][0],  # 'booked'
        help_text="Current status of the ticket"
    )
    passenger = models.ForeignKey(
        Passenger,
        on_delete=models.CASCADE,
        related_name="tickets",
        help_text="Passenger this ticket belongs to"
    )
    berth_allocation = models.CharField(
        max_length=20,
        choices=BERTH_TYPES,
        null=True,
        blank=True,
        help_text="Berth allocated to this ticket"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when ticket was created")

    objects = TicketManager()

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ticket_type", "status"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Ticket for {self.passenger.name} - {self.ticket_type} - {self.status}"


class Berth(models.Model):
    """Model representing a berth in the train."""

    berth_type = models.CharField(
        max_length=20,
        choices=BERTH_TYPES,
        help_text="Type of berth (Lower/Upper/Side)"
    )
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default=AVAILABILITY_STATUS[0][0],  # 'available'
        help_text="Current availability status of the berth",
    )

    class Meta:
        verbose_name = "Berth"
        verbose_name_plural = "Berths"
        ordering = ["berth_type"]
        indexes = [
            models.Index(fields=["availability_status"]),
        ]

    def __str__(self):
        return f"{self.berth_type} - {self.availability_status}"


class TicketHistory(models.Model):
    """Model for tracking ticket status changes."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="history",
        help_text="Ticket whose history is being tracked"
    )
    action = models.CharField(
        max_length=50,
        choices=HISTORY_ACTIONS,
        help_text="Action performed on the ticket"
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the action was performed")

    class Meta:
        verbose_name = "Ticket History"
        verbose_name_plural = "Ticket Histories"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["ticket", "-timestamp"]),
        ]

    def __str__(self):
        return f"Ticket ID: {self.ticket.id} - Action: {self.action} - {self.timestamp}"
