# Example API

A comprehensive FastAPI-based REST API for user management, product catalog, and e-commerce operations. This project demonstrates modern Python web development practices with a focus on clean architecture, comprehensive testing, and robust database management.

## 🚀 Features

- **RESTful API Design**: Follows REST philosophy principles
- **Comprehensive Testing**: Full test coverage with pytest
- **Code Quality**: Linting with pylint and code formatting with black
- **Database Models**: SQLModel-based models with PostgreSQL support
- **User Management**: Complete CRUD operations for user accounts with validation
- **Product Catalog**: Product management with inventory tracking
- **Order System**: Shopping cart, purchase processing, and order lifecycle management
- **Allergy Management**: User allergy tracking and management
- **Interest/Preference System**: User interest and dislike tracking

![Swagger Docs Example](images/api_swagger_v0.1.png)

## 🏗️ Architecture

The project follows a clean, modular architecture:

```
src/
├── db/           # Database models and connection
├── routes/       # API endpoint definitions
├── db_init/      # Database initialization and sample data
└── tests/        # Comprehensive test suite
```

### Core Components

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: Combines SQLAlchemy and Pydantic for type-safe database operations
- **PostgreSQL**: Robust relational database backend
- **Pytest**: Testing framework with coverage reporting

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

## 🛠️ Running the app in Docker

1.  Make sure you have Docker Desktop installed

2.  ```bash
    docker compose up
    ```

## 🛠️ Running the app locally

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd "API Example"
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:

   ```env
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASS=X
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Initialize the database**

   ```bash
   python -m src.db_init.tables_initialize
   ```

## 🚀 Running the Application

### Development Server

```bash
fastapi dev app.py
```

### Production Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)

![API Example](images/api_get_allergy_v0.1.png)

## 🔧 API Endpoints

### Users (`/users`)

- `GET /users` - List all users
- `GET /users/{user_id}` - Get user by ID
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Deactivate user

### Products (`/products`)

- `GET /products` - List all products
- `GET /products/{product_id}` - Get product by ID
- `POST /products` - Create new product
- `PUT /products/{product_id}` - Update product
- `DELETE /products/{product_id}` - Delete product

### Orders (`/orders`)

- `GET /orders` - List all orders
- `GET /orders/{order_id}` - Get order by ID
- `POST /orders` - Create new order
- `PUT /orders/{order_id}` - Update order status

### Allergies (`/allergies`)

- `GET /allergies` - List all allergy types
- `GET /users/{user_id}/allergies` - Get user allergies
- `POST /users/{user_id}/allergies` - Add allergy to user
- `DELETE /users/{user_id}/allergies/{allergy_id}` - Remove allergy from user

### Interests (`/interests`)

- `GET /interests` - List all interest types
- `GET /users/{user_id}/interests` - Get user interests
- `POST /users/{user_id}/interests` - Add interest to user

### Dislikes (`/dislikes`)

- `GET /dislikes` - List all dislike types
- `GET /users/{user_id}/dislikes` - Get user dislikes
- `POST /users/{user_id}/dislikes` - Add dislike to user

## 🧪 Testing

Run the test suite with coverage:

```bash
# Run tests with coverage report
pytest --cov=src

# Run specific test file
pytest tests/routes/test_user.py

```

### Current coverage

![Current Coverage](images/test_cov_v0.1.png)

## 📊 Database Models

### Core Entities

- **User**: Personal information, address, account status
- **Product**: Product details, pricing, inventory
- **Order**: Shopping cart and order management
- **Purchase**: Individual items within orders
- **Allergy**: Predefined allergy options
- **Interest**: User preference categories
- **Dislike**: User aversion categories

### Key Features

- **SQLModel Relationships**: For pythonic cross-table interactions in both One-to-Many and Many-to-Many formats
- **Enum-based Status Tracking**: Order statuses and user conditions
- **Validation**: Phone number validation (E.164 format), email validation
- **Audit Fields**: Creation and update timestamps

## 🔍 Code Quality

The project maintains high code quality standards:

- **Pylint**: Static code analysis and linting
- **Black**: Automatic code formatting
- **Type Hints**: Comprehensive type annotations
- **Docstrings**: Detailed documentation for all functions and classes

## 🚀 Development

### Next project: Building a Frontend

## 📄 License

This project is licensed under the MIT License.

**Built with ❤️ using FastAPI, SQLModel, and modern Python practices**
