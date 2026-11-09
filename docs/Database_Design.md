# MaintainAI Database Design

## PostgreSQL

PostgreSQL stores structured data.

Tables:
- users
- equipment
- maintenance_requests
- work_orders
- work_order_history
- notifications

## MongoDB

MongoDB stores flexible diagnostic information.

Collections:
- fault_analyses

## Database purposes

PostgreSQL manages 
users, equipment, maintenance requests and work orders.

MongoDB stores AI generated fault analyses linked to
their corresponding PostgreSQL maintenance request IDs.

## Application architecture

The React frontend communicates with the Flask backend
through REST APIs.

The Flask backend manages all database interactions.
The frontend never connects directly to either database.