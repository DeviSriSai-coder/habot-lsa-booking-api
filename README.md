# Habot LSA Booking API

**Position:** Python Backend Developer  
**Project:** Habot 1.0 – LSA Service Booking Module  
**Developer:** Devi Sri Sai

## 1. Project Overview

This project is a production-oriented Django REST Framework backend prototype for an LSA (Learning Support Assistant) booking platform.

The system allows parents to:

- Create booking requests for LSAs.
- Search active LSAs by skill and availability.
- Prevent overlapping booking sessions.
- Process payment status updates through a webhook.
- Maintain booking and payment state consistently.
- Run an automated test suite through GitHub Actions.

## 2. Technology Stack

- Python 3.12
- Django
- Django REST Framework
- SQLite for the prototype database
- pytest
- pytest-django
- requests
- GitHub Actions

The application uses Django's MVT architecture with Django REST Framework for REST API endpoints.

## 3. Architecture

The project follows a layered Django structure:

```text
HTTP Request
     |
     v
Django URL Router
     |
     v
DRF API View
     |
     v
Serializer / Validation
     |
     v
Service Layer
     |
     v
Django ORM
     |
     v
Relational Database