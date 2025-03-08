# Railway Ticket Reservation System

A Django-based railway ticket reservation system that handles berth allocation, RAC, and waiting list management.

## System Overview

The system is designed to manage railway ticket reservations, including berth allocation, RAC (Reservation Against Cancellation), and waiting list management. It ensures that passengers are allocated berths based on priority rules and availability.

## System Architecture
The Railway Ticket Reservation System follows a typical Django-based architecture with a PostgreSQL database. Below is an overview of the system architecture:

### Components

1. **Django Application**:
  - **Models**: Define the database schema for passengers, tickets, berths, and ticket history.
  - **Views**: Handle HTTP requests and responses for booking, canceling, and retrieving tickets.
  - **Serializers**: Convert complex data types like querysets and model instances to native Python datatypes.
  - **URLs**: Route URLs to the appropriate views.
  - **Services**: Contain business logic for booking and canceling tickets.
  - **Error Handlers**: Manage custom error responses for various scenarios.

2. **PostgreSQL Database**:
  - Stores data for passengers, tickets, berths, and ticket history.
  - Utilizes Django's ORM for database interactions.

3. **Docker**:
  - **Dockerfile**: Defines the environment for the Django application.
  - **docker-compose.yml**: Manages multi-container Docker applications, including the Django app and PostgreSQL database.

4. **API Documentation**:
  - **Swagger UI**: Provides interactive API documentation.
  - **Redoc UI**: Alternative API documentation interface.

### Data Flow

1. **Booking a Ticket**:
  - The user sends a POST request to the `/tickets/book/` endpoint with passenger details.
  - The request is processed by the `BookTicketView`, which calls the `BookingService`.
  - The `BookingService` validates the request, determines ticket type and berth allocation, and creates the ticket.
  - The response includes the booking details and allocated berths.

2. **Canceling a Ticket**:
  - The user sends a POST request to the `/tickets/cancel/{ticket_id}/` endpoint.
  - The request is processed by the `CancelTicketView`, which calls the `cancel_ticket` service.
  - The service updates the ticket status to canceled and handles any necessary promotions for RAC and waiting list tickets.
  - The response confirms the cancellation.

3. **Retrieving Booked Tickets**:
  - The user sends a GET request to the `/tickets/booked/` endpoint.
  - The request is processed by the `GetBookedTicketsView`, which retrieves all booked tickets from the database.
  - The response includes a list of booked tickets with passenger and berth details.

4. **Retrieving Available Tickets**:
  - The user sends a GET request to the `/tickets/available/` endpoint.
  - The request is processed by the `GetAvailableTicketsView`, which retrieves available berths and quota information.
  - The response includes the count and details of available berths.

### Diagram

```plaintext
+---------------------+       +---------------------+
|  User               |       |  Admin              |
+---------+-----------+       +---------+-----------+
       |                             |
       |                             |
       v                             v
+---------+-----------+       +---------+-----------+
|  Django Views       |       |  Django Admin       |
|  (Book, Cancel,     |       |  Interface          |
|  Retrieve Tickets)  |       +---------+-----------+
+---------+-----------+                 |
       |                             |
       v                             v
+---------+-----------+       +---------+-----------+
|  Django Services    |       |  Django Models      |
|  (Booking,          |       |  (Passenger, Ticket,|
|  Availability)      |       |  Berth, History)    |
+---------+-----------+       +---------+-----------+
       |                             |
       v                             v
+---------+-----------+       +---------+-----------+
|  PostgreSQL Database|       |  API Documentation  |
|  (Data Storage)     |       |  (Swagger, Redoc)   |
+---------------------+       +---------------------+
```


## Database Models

### Passenger

| Field     | Type    | Description                          |
|-----------|---------|--------------------------------------|
| name      | CharField | Full name of the passenger          |
| age       | IntegerField | Age of the passenger              |
| is_child  | BooleanField | Indicates if passenger is under 5 years old |
| gender    | CharField | Gender of the passenger             |

### Ticket

| Field           | Type         | Description                              |
|-----------------|--------------|------------------------------------------|
| ticket_type     | CharField    | Type of ticket (Confirmed/RAC/Waiting List) |
| status          | CharField    | Current status of the ticket             |
| passenger       | ForeignKey   | Passenger this ticket belongs to         |
| berth_allocation| CharField    | Berth allocated to this ticket           |
| created_at      | DateTimeField| Timestamp when ticket was created        |

### Berth

| Field              | Type       | Description                              |
|--------------------|------------|------------------------------------------|
| berth_type         | CharField  | Type of berth (Lower/Upper/Side)         |
| availability_status| CharField  | Current availability status of the berth |

### Ticket History

| Field     | Type         | Description                              |
|-----------|--------------|------------------------------------------|
| ticket    | ForeignKey   | Ticket whose history is being tracked    |
| action    | CharField    | Action performed on the ticket           |
| timestamp | DateTimeField| When the action was performed            |

## Running the Application

To run the Railway Ticket Reservation System application, follow these steps:

### Prerequisites

Ensure you have the following installed:
- Docker
- Docker Compose

### Steps

1. **Clone the Repository:**
  ```sh
  git clone git@github.com:prince-dsd/brisk.git
  cd brisk
  ```

2. **Create a `.env` File:**
  Create a `.env` file in the root directory and add the following environment variables:
  ```env
  SECRET_KEY=<your-secret-key>
  DATABASE_URL=postgres://user:password@db:5432/railway_ticket_db
  ```

3. **Build and Run the Docker Containers:**
  ```sh
  docker-compose up --build
  ```

4. **Apply Migrations:**
  Open a new terminal and run the following command to apply database migrations:
  ```sh
  docker-compose exec app python manage.py migrate
  ```

5. **Create a Superuser:**
  Create a superuser to access the Django admin interface:
  ```sh
  docker-compose exec app python manage.py createsuperuser
  ```

6. **Access the Application:**
  - The application will be available at `http://localhost:8000`
  - The Django admin interface will be available at `http://localhost:8000/admin`

### API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger/`
- Redoc UI: `http://localhost:8000/redoc/`

### Running Tests

To run tests, use the following command:
```sh
docker-compose exec app python manage.py test
```

## Sample Request and Response

### Book Ticket

**Endpoint:** `POST /tickets/book/`

**Request:**
```json
{
  "passengers": [
    {
      "name": "John Doe",
      "age": 30,
      "is_child": false,
      "gender": "Male"
    },
    {
      "name": "Jane Doe",
      "age": 28,
      "is_child": false,
      "gender": "Female"
    }
  ]
}
```

**Response:**
```json
{
  "booking_id": "12345",
  "status": "Confirmed",
  "tickets": [
    {
      "ticket_id": "1",
      "passenger": "John Doe",
      "berth_allocation": "Lower"
    },
    {
      "ticket_id": "2",
      "passenger": "Jane Doe",
      "berth_allocation": "Upper"
    }
  ]
}
```

### Cancel Ticket

**Endpoint:** `POST /tickets/cancel/{ticket_id}/`

**Request:**
```json
{}
```

**Response:**
```json
{
  "message": "Ticket canceled successfully."
}
```

### Get Booked Tickets

**Endpoint:** `GET /tickets/booked/`

**Request:**
```json
{}
```

**Response:**
```json
[
  {
    "ticket_id": "1",
    "passenger": "John Doe",
    "status": "Confirmed",
    "berth_allocation": "Lower"
  },
  {
    "ticket_id": "2",
    "passenger": "Jane Doe",
    "status": "Confirmed",
    "berth_allocation": "Upper"
  }
]
```

### Get Available Tickets

**Endpoint:** `GET /tickets/available/`

**Request:**
```json
{}
```

**Response:**
```json
{
  "available_berths": {
    "Lower": 10,
    "Upper": 5,
    "Side": 3
  },
  "quota_info": {
    "General": 15,
    "Ladies": 3
  }
}
```