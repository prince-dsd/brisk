# Railway Ticket Reservation System

A Django-based railway ticket reservation system that handles berth allocation, RAC, and waiting list management.

## System Overview

The system is designed to manage railway ticket reservations, including berth allocation, RAC (Reservation Against Cancellation), and waiting list management. It ensures that passengers are allocated berths based on priority rules and availability.

## System Architecture

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
+------------v--------------+
|   PostgreSQL Database     |
| (Tickets, Passengers,     |
|  Berths, Waiting List)    |
+---------------------------+

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
  git clone <repository-url>
  cd <repository-directory>
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