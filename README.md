# Django Backend – E-Commerce API

This repository contains the **Django REST API backend** for an e-commerce application.
It provides authentication, product catalog, cart management, and account management endpoints,
designed to be consumed by a **Next.js frontend** using cookie-based JWT authentication.

---

## Features

- Django + Django REST Framework
- JWT authentication (access + refresh tokens)
- Cookie-based auth (httpOnly cookies via Next.js proxy)
- Product catalog with categories
- Shopping cart (one cart per user)
- Account management (email + password updates)
- Seeded test catalog using Platzi Fake Store API
- PostgreSQL database

---

## Tech Stack

- Python 3.12
- Django 5.x
- Django REST Framework
- SimpleJWT
- PostgreSQL
- Requests (for seeding data)

---

## Project Structure

```
Django_backend/
├── Customer_Service_Agentic_AI/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── catalog/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── management/commands/seed_platzi.py
├── cart/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── accounts/
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── manage.py
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd Django_backend
```

### 2. Create and activate a virtual environment
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://ecommerce_user:password@127.0.0.1:5432/ecommerce_db
```

---

## Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Optional: seed test catalog
```bash
python manage.py seed_platzi --limit 200
```

---

## Running the Server

```bash
python manage.py runserver
```

Server runs at:
```
http://127.0.0.1:8000
```

---

## Authentication

JWT via SimpleJWT.

- POST /api/auth/token/
- POST /api/auth/refresh/

Tokens are intended to be stored as **httpOnly cookies** by the Next.js frontend.

---

## API Endpoints

### Products
- GET /api/products/
- GET /api/categories/

### Cart
- GET /api/cart/
- POST /api/cart/items/
- PATCH /api/cart/items/
- DELETE /api/cart/items/
- DELETE /api/cart/

### Account
- GET /api/account/me/
- PATCH /api/account/me/
- POST /api/account/change-password/

---

## Notes

- Intended to be accessed via a Next.js API proxy
- Not production-ready without Gunicorn/Uvicorn and proper settings

---

## License

Personal / educational use.
