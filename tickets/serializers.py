from rest_framework import serializers
from .models import Ticket, Passenger, Berth, TicketHistory

# Passenger Serializer
class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'age', 'is_child']

# Ticket Serializer
class TicketSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer()  # Nested Passenger Serializer

    class Meta:
        model = Ticket
        fields = ['id', 'ticket_type', 'berth_allocation', 'status', 'created_at', 'passenger']

# Berth Serializer
class BerthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Berth
        fields = ['id', 'berth_type', 'availability_status']

# TicketHistory Serializer
class TicketHistorySerializer(serializers.ModelSerializer):
    ticket = TicketSerializer()  # Nested Ticket Serializer

    class Meta:
        model = TicketHistory
        fields = ['id', 'ticket', 'action', 'timestamp']

