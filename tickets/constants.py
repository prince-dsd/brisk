# Ticket Types
CONFIRMED = "confirmed"
RAC = "RAC"
WAITING_LIST = "waiting-list"

TICKET_TYPES = [(CONFIRMED, "Confirmed"), (RAC, "RAC"), (WAITING_LIST, "Waiting List")]

# Ticket Status
BOOKED = "booked"
CANCELED = "canceled"
TICKET_STATUS = [(BOOKED, "Booked"), (CANCELED, "Cancelled")]

# Berth Types
LOWER = "lower"
UPPER = "upper"
SIDE_LOWER = "side-lower"
SIDE_UPPER = "side-upper"

BERTH_TYPES = [
    (LOWER, "Lower"),
    (SIDE_LOWER, "Side-Lower"),
    (UPPER, "Upper"),
    (SIDE_UPPER, "Side-Upper")
]

# Availability Status
AVAILABLE = "available"
BOOKED = "booked"
RESERVED = "reserved"

AVAILABILITY_STATUS = [
    (AVAILABLE, "Available"),
    (BOOKED, "Booked"),
    (RESERVED, "Reserved")
]

# Error Messages
TICKET_NOT_FOUND = "Ticket not found."
ALREADY_CANCELED = "This ticket is already canceled."
NO_CONFIRMED_BERTHS = "No confirmed berths available"
NO_RAC_BERTHS = "No RAC berths available"
NO_TICKETS_AVAILABLE = "No tickets available"
NO_BERTH_AVAILABLE = "No available berths for this ticket."
REQUIRED_FIELDS = "All fields are required."

# Success Messages
ACTION_CANCELED = "Ticket canceled successfully."

# History Actions
ACTION_BOOKED = "booked"
ACTION_CANCELED = "canceled"
ACTION_MOVED_RAC = "moved_to_RAC"
ACTION_PROMOTED_RAC = "promoted_from_RAC"
ACTION_PROMOTED_WAITING = "promoted_from_waiting"

HISTORY_ACTIONS = [
    (ACTION_BOOKED, "Booked"),
    (ACTION_CANCELED, "Canceled"),
    (ACTION_MOVED_RAC, "Moved to RAC"),
    (ACTION_PROMOTED_WAITING, "Promoted from Waiting List"),
]

# Gender
GENDER_MALE = "M"
GENDER_FEMALE = "F"
GENDER_CHOICES = [(GENDER_MALE, "Male"), (GENDER_FEMALE, "Female")]

# Age Limits
SENIOR_AGE = 60
CHILD_AGE = 5

# Ticket Limits
CONFIRMED_BERTH_LIMIT = 63  # Regular berths (18 + 18 + 18 + 9)
RAC_TICKET_LIMIT = 9      # Side lower berths
WAITING_LIST_LIMIT = 10    # Waiting list capacity
