# Data Saver

A FastAPI-based CRUD web application for managing users with login, registration, update, delete, and logout features.

## Features

- User login and logout
- Register new users
- View all users in a table
- Edit and delete user records
- Responsive UI
- SQLite database

## Tech Stack

- FastAPI
- Jinja2 templates
- SQLAlchemy
- SQLite
- HTML, CSS

## Project Structure

- `app/main.py` - FastAPI app entry point
- `app/crud.py` - Route handlers and business logic
- `app/database.py` - Database setup
- `app/models.py` - SQLAlchemy models
- `app/templates/` - HTML templates
- `app/static/` - CSS and static assets

## Requirements

Install the dependencies used by the app:

```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart itsdangerous
```

## Run Locally

1. Clone the repository:

```bash
git clone https://github.com/srinivas019/Datasaver.git
cd Datasaver
```

2. Create and activate a virtual environment:

```bash
python -m venv env
env\Scripts\activate
```

3. Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart itsdangerous
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

5. Open the browser:

```bash
http://127.0.0.1:8000
```

## Notes

- The SQLite database file is created automatically as `users.db`.
- The app uses session-based login.
- For deployment, set a secure session secret key with environment variables.

## License

No license has been specified yet.
