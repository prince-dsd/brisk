### **System Overview**

This Railway Ticket Reservation System manages bookings, cancellations, and the availability of railway tickets. It includes seat allocation for confirmed berths, RAC (Reservation Against Cancellation), and waiting-list tickets, with specific rules for priority seating based on passenger attributes (e.g., elderly, ladies with children). The system will use Django for the backend, PostgreSQL as the database, and Django's ORM for database management.

### **System Architecture**

```
                +---------------------------+
                |        Web Client         |
                |  (Postman, Browser, etc.) |
                +------------+--------------+
                             |
                             | REST API (Django REST Framework)
                             |
                +------------v--------------+
                |     Django Backend        |
                | (REST API with DRF)       |
                +------------+--------------+
                             |
              +--------------+-----------------------+
              |                                      |
   +----------v-----------+              +-----------v-----------+
   |   PostgreSQL Database|              |   Cache Layer (optional)|
   |  (Tickets, Passengers,|              |  (For Fast Access to    |
   |   Berths, Waiting List|              |    Availability Data)  |
   +-----------------------+              +------------------------+
```

### **Django Components**
- **Django REST Framework (DRF)**: For building the API endpoints.
- **PostgreSQL**: A relational database to store the details about passengers, tickets, berths, and the waiting list.
- **Celery** (Optional): To handle tasks like sending email notifications, managing scheduled promotions, etc.

---

### **Database Schema**

Here’s a description of the tables we will use for this system:

#### **Table: Passengers**

| Column        | Data Type    | Description                                  |
|---------------|--------------|----------------------------------------------|
| `id`          | INT          | Primary Key, Unique ID for each passenger    |
| `name`        | VARCHAR(255)  | Passenger’s full name                        |
| `age`         | INT          | Passenger's age                              |
| `is_child`    | BOOLEAN      | Whether the passenger is a child (age < 5)   |
| `ticket_id`   | INT          | Foreign Key, references `Ticket` table       |

#### **Table: Tickets**

| Column         | Data Type   | Description                                        |
|----------------|-------------|----------------------------------------------------|
| `id`           | INT         | Primary Key, Unique ID for each ticket            |
| `status`       | ENUM        | Ticket status (`confirmed`, `RAC`, `waiting-list`) |
| `berth_type`   | ENUM        | Berth type (`upper`, `lower`, `side-lower`)       |
| `priority`     | ENUM        | Priority group (`normal`, `senior`, `lady-child`) |
| `passenger_count` | INT       | Number of passengers in the ticket               |
| `seat_number`  | INT         | Seat number assigned to the ticket                |

#### **Table: BerthAllocations**

| Column        | Data Type    | Description                                     |
|---------------|--------------|-------------------------------------------------|
| `ticket_id`   | INT          | Foreign Key, references `Tickets` table        |
| `berth_type`  | ENUM         | Berth type allocated (`upper`, `lower`, etc.)  |
| `is_occupied` | BOOLEAN      | Flag indicating whether the berth is occupied  |

#### **Table: WaitingList**

| Column         | Data Type  | Description                                      |
|----------------|------------|--------------------------------------------------|
| `ticket_id`    | INT        | Foreign Key, references `Tickets` table         |
| `position_in_queue` | INT    | Position in the waiting list                    |
| `is_promoted`  | BOOLEAN    | Flag indicating whether the ticket has been promoted from the waiting list to RAC |

---

### **Concurrency Handling**

- **Database Locking**: Django ORM supports transactions, so you can use `select_for_update` to lock rows when booking tickets to avoid double booking.

  Example:
  ```python
  from django.db import transaction
  with transaction.atomic():
      ticket = Ticket.objects.select_for_update().get(id=ticket_id)
  ```

---

### **1. Overview**

The Railway Ticket Reservation System is a platform designed to handle ticket reservations, cancellations, and viewing available/booked tickets. The system adheres to specific rules regarding seat allocation and prioritization, including handling the **Confirmed Berths**, **RAC (Reservation Against Cancellation)**, and **Waiting List**.

---

### **2. Architecture Diagram**

#### **2.1 High-Level Architecture**

```plaintext
+------------------------------------+
|           User/Client (Browser)    |
+------------------------------------+
                |
                v
+------------------------------------+
|           API Gateway (Django)     |
|      Handles Requests/Responses    |
+------------------------------------+
                |
                v
+------------------------------------+     +-----------------------------------+
|         Django REST Framework      |<--->|     PostgreSQL Database          |
|  (API Views, Serializers, Models)  |     |  (Stores Tickets, Passengers,    |
|                                    |     |    Berth Allocations, etc.)      |
+------------------------------------+     +-----------------------------------+
```

- **User/Client**: The users access the system via HTTP requests (POST for booking, GET for viewing tickets, etc.). This could be via a frontend app or Postman for testing.
- **API Gateway**: The Django application is the API gateway that handles incoming requests. It processes the business logic related to ticket reservations and communicates with the database.
- **Django REST Framework**: The API is implemented using Django and Django REST Framework (DRF). It allows us to build RESTful APIs for interacting with the ticket reservations.
- **PostgreSQL Database**: The database holds all the data, including **Passengers**, **Tickets**, and **Berth Allocations**. It is queried by the Django app to retrieve and store data.

---

### **3. Database Schema Diagram**

Here’s the structure of the key database models and how they relate to each other:

```plaintext
+-------------------+          +-------------------+
|   Passenger       |          |   Ticket          |
+-------------------+          +-------------------+
| id (PK)           | <-------> | id (PK)           |
| name              |          | passenger_id (FK) |
| age               |          | status            |
| is_child          |          | berth_type        |
| is_priority       |          | created_at        |
+-------------------+          +-------------------+
```

#### **Explanation**:
- **Passenger**: Represents a passenger. Contains details like `name`, `age`, `is_child` (whether the passenger is a child under 5 years old), and `is_priority` (for elderly passengers or women with children).

- **Ticket**: Represents the ticket issued to a passenger. It stores the `status` of the ticket (Booked, RAC, Waiting), `berth_type` (Side-lower, Lower Berth, etc.), and a reference to the `passenger`.

---

### **4. Flowchart for Booking and Cancellation**

#### **4.1 Booking Process**

```plaintext
+-------------------+
|  Start Booking    |
+-------------------+
        |
        v
+-------------------+
|  Validate Input   |
|  (Passenger Data) |
+-------------------+
        |
        v
+-------------------+
|  Check Seat Availability |
+-------------------+
        |
        v
+-------------------+    No    +-------------------+
|   Available?      | --------> | Show "No Tickets  |
+-------------------+          |    Available"     |
        |                       +-------------------+
   Yes v
+-------------------+
|  Allocate Berth   |
+-------------------+
        |
        v
+-------------------+
|  Save Ticket to DB |
+-------------------+
        |
        v
+-------------------+
|   End Booking     |
+-------------------+
```

#### **4.2 Cancellation Process**

```plaintext
+-------------------+
|  Start Cancellation|
+-------------------+
        |
        v
+-------------------+
|  Validate Ticket  |
|  (Ticket ID)      |
+-------------------+
        |
        v
+-------------------+
|  Ticket Found?    |
+-------------------+
        |
        v
  Yes  +-------------------+
        |  Change Ticket    |
        |  Status to CANCEL |
        +-------------------+
        |
        v
+-------------------+
|  Promote RAC to   |
|  Confirmed Berth  |
+-------------------+
        |
        v
+-------------------+
|  End Cancellation |
+-------------------+
```

---

### **5. API Endpoints & Sample Requests**

Below are the **API endpoints**, their **HTTP methods**, and sample requests for booking, canceling, and viewing tickets.

---

#### **5.1 `POST /api/v1/tickets/book` - Book a Ticket**

**Description**: This endpoint is used to book a new ticket. It accepts passenger data and berth preference.

**Request:**
```http
POST /api/v1/tickets/book HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "passenger": {
    "name": "John Doe",
    "age": 65,
    "is_child": false,
    "is_priority": true
  },
  "berth_type": "LOWER"
}
```

**Response:**
```json
{
  "id": 1,
  "passenger": {
    "id": 1,
    "name": "John Doe",
    "age": 65,
    "is_child": false,
    "is_priority": true
  },
  "status": "BOOKED",
  "berth_type": "LOWER",
  "created_at": "2025-03-06T10:00:00Z"
}
```

---

#### **5.2 `POST /api/v1/tickets/cancel/{ticketId}` - Cancel a Ticket**

**Description**: This endpoint is used to cancel an existing ticket. If a ticket is canceled, it checks if any RAC or Waiting List passengers need to be upgraded.

**Request:**
```http
POST /api/v1/tickets/cancel/1 HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "message": "Ticket canceled successfully"
}
```

---

#### **5.3 `GET /api/v1/tickets/booked` - Get All Booked Tickets**

**Description**: This endpoint returns a list of all tickets that are confirmed.

**Request:**
```http
GET /api/v1/tickets/booked HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
[
  {
    "id": 1,
    "passenger": {
      "id": 1,
      "name": "John Doe",
      "age": 65,
      "is_child": false,
      "is_priority": true
    },
    "status": "BOOKED",
    "berth_type": "LOWER",
    "created_at": "2025-03-06T10:00:00Z"
  }
]
```

---

#### **5.4 `GET /api/v1/tickets/available` - Get All Available Tickets**

**Description**: This endpoint returns a list of all waiting list tickets (those that haven’t been booked yet).

**Request:**
```http
GET /api/v1/tickets/available HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
[
  {
    "id": 2,
    "passenger": {
      "id": 2,
      "name": "Jane Doe",
      "age": 30,
      "is_child": false,
      "is_priority": false
    },
    "status": "WAITING",
    "berth_type": "SIDE-LOWER",
    "created_at": "2025-03-06T10:05:00Z"
  }
]
```

---

### **6. Advanced Concepts:**

#### **6.1 Handling Concurrency**

- **Optimistic Locking**: Implement optimistic concurrency control using Django's `select_for_update()` to prevent two users from booking the same seat simultaneously.
- **Atomic Transactions**: Ensure that the seat allocation process (booking or cancellation) is wrapped in an atomic transaction using Django's `@transaction.atomic` decorator. This ensures that if anything goes wrong (e.g., a seat is double-booked), all changes are rolled back.

#### **6.2 Error Handling**

- If the user tries to book a ticket when the capacity (confirmed berths + RAC) is full, the API should return an error message: `"No tickets available"`.
- If a ticket ID for cancellation doesn't exist, a 404 response should be returned with the message: `"Ticket not found"`.

---

### **7. Conclusion**

This documentation provides a thorough breakdown of the system’s architecture, flowcharts, and API endpoints for the Railway Ticket Reservation System. It outlines the main components and their interactions, such as the API Gateway, the database schema, and sample requests for each endpoint. The design ensures a flexible, efficient, and maintainable system.