from .models import Ticket, TicketHistory

def cancel_ticket(ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return None, "Ticket not found."

    if ticket.status == 'canceled':
        return None, "This ticket is already canceled."

    ticket.status = 'canceled'
    ticket.save()

    handle_promotions(ticket)

    # Create cancellation history
    TicketHistory.objects.create(ticket=ticket, action='canceled')

    return ticket, None

def handle_promotions(ticket):
    if ticket.ticket_type == 'confirmed':
        promote_next_rac_ticket()

    promote_next_waiting_list_ticket()

def promote_next_rac_ticket():
    next_rac_ticket = Ticket.objects.filter(ticket_type='RAC', status='booked').first()
    if next_rac_ticket:
        next_rac_ticket.ticket_type = 'confirmed'
        next_rac_ticket.save()
        TicketHistory.objects.create(ticket=next_rac_ticket, action='promoted_from_RAC')

def promote_next_waiting_list_ticket():
    waiting_list_ticket = Ticket.objects.filter(ticket_type='waiting-list', status='booked').first()
    if waiting_list_ticket:
        waiting_list_ticket.ticket_type = 'RAC'
        waiting_list_ticket.save()
        TicketHistory.objects.create(ticket=waiting_list_ticket, action='moved_to_RAC')