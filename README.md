# Library Management System

A RESTful API for managing a library, built with FastAPI and SQLite. This project fulfills all requirements for the Module 3 Project 2, including CRUD operations, authentication, a business logic endpoint, automated tests, and a Postman collection.

## Features
- **CRUD Operations**: Manage users, books, and borrow records
- **Authentication**: JWT-based user registration and login
- **Authorization**: Role-based access (admin vs. regular users)
- **Business Logic**: Personalized book recommendations based on borrowing history
- **Testing**: Automated tests with pytest and manual testing with Postman
- **Code Quality**: Pylint report for code quality assessment

## Setup
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Prerequisites
- Python 3.9+
- Git
- Postman (optional, for manual testing)

### Installation
1. Clone the repository:
```bash
git clone git@github.com:FurtakED/Library_management_system.git
cd Library_management_system
```
