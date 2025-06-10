# LinkVault

LinkVault is a web application designed to help you create, organize, and manage your bookmarks efficiently. You can group bookmarks into categories, making it easier to find and access your favorite links. The project emphasizes clean and well-structured code, especially in the Django views and module organization.

## Features

- User authentication (Google OAuth, email verification)
- Create, edit, and delete bookmarks
- Organize bookmarks into categories
- Clean and maintainable Django views
- Dockerized deployment with Nginx
- Environment variables management
- Logging support for analytics and debugging

## Technologies Used

- Django
- Django session management
- django-email-verification
- Google OAuth
- Docker
- Nginx
- environ
- JavaScript (for interactivity)
- Logging infrastructure

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- (Optional) Python 3.10+ and pip if running locally without Docker

### Quick Start with Docker

1. Clone the repository:
    ```bash
    git clone https://github.com/kadyevsultan/LinkVault.git
    cd LinkVault
    ```
2. Copy the example environment variables and edit as needed:
    ```bash
    cp web/.env.example web/.env
    ```
3. Build and start the application:
    ```bash
    docker-compose up --build
    ```
4. The application will be available at `http://localhost`

### Manual Setup (Without Docker)

1. Set up a Python virtual environment and install requirements:
    ```bash
    cd web
    python -m venv venv
    source venv/bin/activate
    pip install -r req.txt
    ```
2. Configure environment variables in `web/.env`
3. Run migrations and start the server:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

## Code Structure

- `web/` - Django project root
  - `accounts/` - User authentication and profiles
  - `links/` - Bookmark models, views, and logic
  - `linkvault/` - Project settings, URLs, static files
  - `templates/` - HTML templates
  - `static/` - Static assets
- `nginx/` - Nginx configuration for production
- `docker-compose.yml` - Multi-service orchestration

## Notable Details

- Views are designed to be as clean and maintainable as possible
- Modules are well-structured for scalability
- Email verification and Google OAuth for secure authentication

## License

This project is open-source. License information coming soon.

---

Feel free to open issues or contribute!
