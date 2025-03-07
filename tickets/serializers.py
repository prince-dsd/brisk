from rest_framework import serializers

from .models import Berth, Passenger, Ticket, TicketHistory


class PassengerSerializer(serializers.ModelSerializer):
    """Serializer for passenger information."""

    class Meta:
        model = Passenger
        fields = ["id", "name", "age", "is_child", "gender"]
        read_only_fields = ["is_child"]  # is_child is automatically set based on age


class BerthSerializer(serializers.ModelSerializer):
    """Serializer for berth information."""

    class Meta:
        model = Berth
        fields = ["id", "berth_type", "availability_status"]
        read_only_fields = ["availability_status"]  # Status is managed by the system


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for ticket information with nested passenger details."""

    passenger = PassengerSerializer()
    berth_details = BerthSerializer(source="berth", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "ticket_type", "status", "berth_allocation", "berth_details", "created_at", "passenger"]
        read_only_fields = ["status", "berth_allocation", "created_at"]

    def create(self, validated_data):
        """Create a ticket with nested passenger data."""
        passenger_data = validated_data.pop("passenger")
        passenger = Passenger.objects.create(**passenger_data)
        ticket = Ticket.objects.create(passenger=passenger, **validated_data)
        return ticket

    def update(self, instance, validated_data):
        """Update a ticket with nested passenger data."""
        passenger_data = validated_data.pop("passenger", None)
        if passenger_data:
            for attr, value in passenger_data.items():
                setattr(instance.passenger, attr, value)
            instance.passenger.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TicketHistorySerializer(serializers.ModelSerializer):
    """Serializer for ticket history with nested ticket details."""

    ticket = TicketSerializer(read_only=True)

    class Meta:
        model = TicketHistory
        fields = ["id", "ticket", "action", "timestamp"]
        read_only_fields = ["timestamp"]

    def to_representation(self, instance):
        """Customize the history representation."""
        representation = super().to_representation(instance)
        representation["action_display"] = instance.get_action_display()
        return representation
