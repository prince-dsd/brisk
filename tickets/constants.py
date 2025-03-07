# Ticket Types
TICKET_TYPES = [("confirmed", "Confirmed"), ("RAC", "RAC"), ("waiting-list", "Waiting List")]

# Ticket Status
TICKET_STATUS = [("booked", "Booked"), ("cancelled", "Cancelled")]

# Berth Types
BERTH_TYPES = [("lower", "Lower"), ("side-lower", "Side-Lower"), ("upper", "Upper"), ("side-upper", "Side-Upper")]

# Availability Status
AVAILABILITY_STATUS = [("available", "Available"), ("booked", "Booked"), ("reserved", "Reserved")]

# Error Messages
TICKET_NOT_FOUND = "Ticket not found."
ALREADY_CANCELED = "This ticket is already canceled."
NO_CONFIRMED_BERTHS = "No confirmed berths available"
NO_RAC_BERTHS = "No RAC berths available"
NO_TICKETS_AVAILABLE = "No tickets available"
NO_BERTH_AVAILABLE = "No available berths for this ticket."
REQUIRED_FIELDS = "All fields are required."

# Success Messages
CANCEL_SUCCESS = "Ticket canceled successfully."

# History Actions
HISTORY_ACTIONS = [
    ("booked", "Booked"),
    ("canceled", "Canceled"),
    ("moved_to_RAC", "Moved to RAC"),
    ("promoted_from_waiting", "Promoted from Waiting List"),
]

# Gender
GENDER_FEMALE = "F"

# Age Limits
SENIOR_AGE = 60
CHILD_AGE = 5
