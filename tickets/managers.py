from django.db import models

class TicketManager(models.Manager):
    def check_confirmed_berths_limit(self):
        """
        Check if the number of confirmed berths is less than 63.
        """
        confirmed_count = self.filter(ticket_type='confirmed').count()
        if confirmed_count >= 63:
            raise ValidationError("Cannot book more than 63 confirmed berths.")

    def check_rac_limit(self):
        """
        Check if the number of RAC tickets is less than 18.
        """
        rac_count = self.filter(ticket_type='RAC').count()
        if rac_count >= 18:
            raise ValidationError("Cannot book more than 18 RAC tickets.")

    def check_waiting_list_limit(self):
        """
        Check if the number of waiting list tickets is less than 10.
        """
        waiting_list_count = self.filter(ticket_type='waiting-list').count()
        if waiting_list_count >= 10:
            raise ValidationError("Cannot add more than 10 waiting-list tickets.")
    
    def assign_berth_based_on_priority(self, passenger):
        """
        Assign a berth based on the priority logic.
        """
        lower_berths = Berth.objects.filter(berth_type='lower', availability_status='available')
        if passenger.age >= 60 or (passenger.age < 5 and passenger.is_child):
            if lower_berths.exists():
                return lower_berths.first()

        side_lower_berths = Berth.objects.filter(berth_type='side-lower', availability_status='available')
        if side_lower_berths.exists():
            return side_lower_berths.first()

        available_berths = Berth.objects.filter(availability_status='available')
        if available_berths.exists():
            return available_berths.first()

        return None
