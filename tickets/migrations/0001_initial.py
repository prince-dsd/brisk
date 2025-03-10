# Generated by Django 3.2.25 on 2025-03-07 10:29

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Berth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('berth_type', models.CharField(choices=[('lower', 'Lower'), ('side-lower', 'Side-Lower'), ('upper', 'Upper'), ('side-upper', 'Side-Upper')], help_text='Type of berth (Lower/Upper/Side)', max_length=20)),
                ('availability_status', models.CharField(choices=[('available', 'Available'), ('booked', 'Booked'), ('reserved', 'Reserved')], default='available', help_text='Current availability status of the berth', max_length=20)),
            ],
            options={
                'verbose_name': 'Berth',
                'verbose_name_plural': 'Berths',
                'ordering': ['berth_type'],
            },
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Full name of the passenger', max_length=255)),
                ('age', models.IntegerField(help_text='Age of the passenger', validators=[django.core.validators.MinValueValidator(0)])),
                ('is_child', models.BooleanField(default=False, help_text='Indicates if passenger is under 5 years old')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], help_text='Gender of the passenger', max_length=1)),
            ],
            options={
                'verbose_name': 'Passenger',
                'verbose_name_plural': 'Passengers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_type', models.CharField(choices=[('confirmed', 'Confirmed'), ('RAC', 'RAC'), ('waiting-list', 'Waiting List')], help_text='Type of ticket (Confirmed/RAC/Waiting List)', max_length=20)),
                ('status', models.CharField(choices=[('booked', 'Booked'), ('cancelled', 'Cancelled')], default='booked', help_text='Current status of the ticket', max_length=20)),
                ('berth_allocation', models.CharField(blank=True, help_text='Berth allocated to this ticket', max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when ticket was created')),
                ('passenger', models.ForeignKey(help_text='Passenger this ticket belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='tickets.passenger')),
            ],
            options={
                'verbose_name': 'Ticket',
                'verbose_name_plural': 'Tickets',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TicketHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('booked', 'Booked'), ('canceled', 'Canceled'), ('moved_to_RAC', 'Moved to RAC'), ('promoted_from_waiting', 'Promoted from Waiting List')], help_text='Action performed on the ticket', max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='When the action was performed')),
                ('ticket', models.ForeignKey(help_text='Ticket whose history is being tracked', on_delete=django.db.models.deletion.CASCADE, related_name='history', to='tickets.ticket')),
            ],
            options={
                'verbose_name': 'Ticket History',
                'verbose_name_plural': 'Ticket Histories',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='berth',
            index=models.Index(fields=['availability_status'], name='tickets_ber_availab_d7372e_idx'),
        ),
        migrations.AddIndex(
            model_name='tickethistory',
            index=models.Index(fields=['ticket', '-timestamp'], name='tickets_tic_ticket__7cebb9_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['ticket_type', 'status'], name='tickets_tic_ticket__73a594_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['status'], name='tickets_tic_status_0e5646_idx'),
        ),
    ]
