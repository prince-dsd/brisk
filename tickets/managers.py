from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models


class TicketManager(models.Manager):
    CONFIRMED_BERTHS_LIMIT = 63
    RAC_LIMIT = 18
    WAITING_LIST_LIMIT = 10

    def check_confirmed_berths_limit(self):
        """
        Check if the number of confirmed berths is less than the limit.
        """
        try:
            confirmed_count = self.filter(ticket_type="confirmed").count()
            if confirmed_count >= self.CONFIRMED_BERTHS_LIMIT:
                raise ValidationError(f"Cannot book more than {self.CONFIRMED_BERTHS_LIMIT} confirmed berths.")
        except Exception as e:
            raise ValidationError(f"Error checking confirmed berths limit: {str(e)}")

    def check_rac_limit(self):
        """
        Check if the number of RAC tickets is less than the limit.
        """
        try:
            rac_count = self.filter(ticket_type="RAC").count()
            if rac_count >= self.RAC_LIMIT:
                raise ValidationError(f"Cannot book more than {self.RAC_LIMIT} RAC tickets.")
        except Exception as e:
            raise ValidationError(f"Error checking RAC limit: {str(e)}")

    def check_waiting_list_limit(self):
        """
        Check if the number of waiting list tickets is less than the limit.
        """
        try:
            waiting_list_count = self.filter(ticket_type="waiting-list").count()
            if waiting_list_count >= self.WAITING_LIST_LIMIT:
                raise ValidationError(f"Cannot add more than {self.WAITING_LIST_LIMIT} waiting-list tickets.")
        except Exception as e:
            raise ValidationError(f"Error checking waiting list limit: {str(e)}")

    def assign_berth_based_on_priority(self, passenger):
        """
        Assign a berth based on the priority logic.
        """
        try:
            if passenger.age >= 60 or (passenger.age < 5 and passenger.is_child):
                return self._get_available_berth("lower")

            return self._get_available_berth("side-lower") or self._get_available_berth() or None
        except Exception as e:
            raise ValidationError(f"Error assigning berth based on priority: {str(e)}")

    def _get_available_berth(self, berth_type=None):
        """
        Helper method to get an available berth of a specific type or any type.
        """
        try:
            Berth = apps.get_model("tickets", "Berth")
            query = {"availability_status": "available"}
            if berth_type:
                query["berth_type"] = berth_type

            return Berth.objects.filter(**query).first()
        except Exception as e:
            raise ValidationError(f"Error getting available berth: {str(e)}")
