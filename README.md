# FitAct

## Overview

FitAct is a full-stack web-based fitness platform designed to guide users from fitness awareness to practical action. The platform addresses a common problem: many people know that exercise is important but struggle to choose a suitable workout programme, feel overwhelmed by options, and lack structured support, progress tracking, and motivation to remain consistent.

FitAct solves this by providing a personalised, recommendation-driven fitness platform that allocates users to suitable workout programmes based on their goals and experience level. The system supports workout browsing, custom workout creation, workout execution and logging, progress tracking, and milestone-based achievement badges.

This application is an artefact produced as part of a final-year dissertation at Newcastle University.

- **Student Number:** 230266971
- **Student Name:** Amro Mohammed A Jamal
- **Module:** CSC3094 — Computer Science Dissertation

---

## Project Structure

```
FitAct_CSC3094_Dissertation/
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml               # GitHub Actions CI/CD pipeline
│
├── app/                            # Main Flask application package
│   ├── __init__.py                 # Application factory (create_app)
│   ├── extensions.py               # Flask extension instances (db, bcrypt, login_manager)
│   ├── models.py                   # SQLAlchemy database models
│   │
│   ├── achievements/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Achievements and milestone badge routes
│   │
│   ├── auth/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Registration, login, and logout routes
│   │
│   ├── exercises/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Exercise guidance routes
│   │
│   ├── main/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Home, account, profile, and password routes
│   │
│   ├── programme/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Programme viewing and manual selection routes
│   │
│   ├── progress/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Past workout logs, edit and delete routes
│   │
│   ├── questionnaire/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Onboarding questionnaire and recommendation engine
│   │
│   ├── security/
│   │   ├── __init__.py             # Empty package init
│   │   └── firewall.py             # Firewall rules for SQL injection, XSS, path traversal
│   │
│   ├── tracking/
│   │   ├── __init__.py             # Empty package init
│   │   └── routes.py               # Workout execution, logging, and badge award logic
│   │
│   ├── utils/
│   │   ├── __init__.py             # Empty package init
│   │   └── validators.py           # Password policy validation utilities
│   │
│   └── workouts/
│       ├── __init__.py             # Empty package init
│       └── routes.py               # Workout page, repository, saved workouts, custom workouts
│
├── migrations/                     # Flask-Migrate database migration files
│
├── static/
│   ├── css/
│   │   └── style.css               # Global FitAct stylesheet
│   ├── images/
│   │   ├── logo.png                # FitAct dumbbell logo
│   │   └── badge_trophy.png        # Achievement badge image
│   └── js/
│       └── main.js                 # Global JavaScript
│
├── templates/
│   ├── base.html                   # Shared base template with navigation
│   ├── achievements/
│   │   └── achievements.html       # Milestones and badges page
│   ├── auth/
│   │   ├── login.html              # Login page
│   │   ├── register.html           # Registration page with live password checklist
│   │   └── register_success.html   # Registration success confirmation
│   ├── errors/
│   │   ├── 400.html                # Bad Request error page
│   │   ├── 404.html                # Not Found error page
│   │   ├── 500.html                # Internal Server Error page
│   │   ├── 501.html                # Not Implemented error page
│   │   └── firewall_blocked.html   # Firewall attack detection page
│   ├── exercises/
│   │   └── guidance.html           # Exercise guidance detail page
│   ├── main/
│   │   ├── account.html            # User account page
│   │   ├── change_password.html    # Change password page
│   │   └── edit_profile.html       # Edit profile page
│   ├── programme/
│   │   ├── change_programme.html   # Manual programme selection page
│   │   ├── programme.html          # My Programme page
│   │   ├── programme_preview.html  # Programme preview page
│   │   └── workout_preview.html    # Workout preview within a programme
│   ├── progress/
│   │   ├── edit_log.html           # Edit a logged workout
│   │   └── progress.html           # Progress and past workouts page
│   ├── questionnaire/
│   │   ├── confirm.html            # Programme recommendation confirmation
│   │   └── questionnaire.html      # Onboarding questionnaire page
│   ├── tracking/
│   │   └── execute.html            # Workout execution and logging page
│   └── workouts/
│       ├── change_workout.html     # Change today's workout page
│       ├── create_custom.html      # Create custom workout page
│       ├── edit_custom.html        # Edit custom workout page
│       ├── repository.html         # Workout repository page
│       ├── saved.html              # Saved workouts page
│       ├── workout_info.html       # Workout detail and info page
│       └── workout_page.html       # Main workout page (Today's Workout)
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Pytest fixtures and test configuration
│   ├── test_placeholder.py         # Basic app creation and route tests
│   ├── test_auth.py                # Authentication route tests
│   ├── test_achievements.py        # Achievements route tests
│   ├── test_exercises.py           # Exercise guidance route tests
│   ├── test_programme.py           # Programme route tests
│   ├── test_recommendation.py      # Recommendation engine tests
│   ├── test_tracking.py            # Workout tracking and logging tests
│   └── test_workouts.py            # Workout repository and saved workouts tests
│
├── .env                            # Environment variables (not committed to Git)
├── .gitignore                      # Git ignore rules
├── config.py                       # Flask configuration classes
├── docker-compose.yml              # Docker Compose for local deployment and scaling
├── Dockerfile                      # Docker image build instructions
├── nginx.conf                      # Nginx reverse proxy and load balancer config
├── requirements.txt                # Python dependencies
├── run.py                          # Application entry point
└── seed.py                         # Database seeding script for predefined data
```

---

## Running the Application Locally

### Prerequisites

- Python 3.10+
- PostgreSQL running locally
- A virtual environment set up

### Setup

**1. Clone the repository:**

```bash
git clone https://github.com/c3026697/FitAct_CSC3094_Dissertation.git
cd FitAct_CSC3094_Dissertation
```

**2. Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Configure your `.env` file:**

Make sure your `.env` file at the project root contains the following. When running locally, use the local database URL and comment out the Docker one:

```env
SECRET_KEY=08f36aaeb32324795b15dcf9d01478d800f5adcdaea3f47a7b7b013b548f626e

# Local database (use this when running locally)
DATABASE_URL=postgresql://postgres:password@localhost:5432/fitact_db

# Docker database (use this when running via Docker — comment out the line above)
# DATABASE_URL=postgresql://postgres:password@host.docker.internal:5432/fitact_db
```

**5. Run database migrations:**

```bash
flask db upgrade
```

**6. Seed the database with predefined programmes and exercises:**

```bash
python seed.py
```

**7. Start the application:**

```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

---

## Running the Application with Docker

### Prerequisites

- Docker Desktop installed and running
- Docker Compose available

### Local Deployment (NFR6)

**1. Ensure your `.env` file uses `host.docker.internal` for the database URL:**

```env
SECRET_KEY=your-secret-key-here

# Comment out the local URL:
# DATABASE_URL=postgresql+psycopg2://your_user:your_password@localhost:5432/fitact_db

# Use this for Docker:
DATABASE_URL=postgresql+psycopg2://your_user:your_password@host.docker.internal:5432/fitact_db
```

**2. Build the Docker image locally:**

```bash
docker build -t fitact:latest .
```

Or pull the latest image from GitHub Container Registry (authentication required):

```bash
docker login ghcr.io -u your-github-username -p your-github-pat
docker pull ghcr.io/c3026697/fitact_csc3094_dissertation/fitact:latest
```

**3. Start the application:**

```bash
docker compose up
```

Visit `http://localhost:8080` in your browser.

**4. Stop the application:**

```bash
docker compose down
```

### Horizontal Scaling (NFR7)

To demonstrate horizontal scalability with Nginx load balancing across multiple container instances:

```bash
docker compose up --scale app=3
```

Verify all instances are running:

```bash
docker compose ps
```

You should see 3 `app` instances and 1 `web` (Nginx) instance. Nginx automatically distributes incoming traffic across all running app containers.

---

## Accessing the PostgreSQL Database via DBeaver

DBeaver is a free database administration tool that can be used to inspect and manage the FitAct PostgreSQL database.

### Steps

1. Download and install [DBeaver](https://dbeaver.io/download/)
2. Open DBeaver and click **New Database Connection**
3. Select **PostgreSQL** and click **Next**
4. Enter the following connection details:

| Field | Value |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `fitact_db` |
| Username | *(inject your PostgreSQL username here)* |
| Password | *(inject your PostgreSQL password here)* |

5. Click **Test Connection** to verify
6. Click **Finish** to save the connection

Once connected, you can browse tables, run SQL queries, and inspect all FitAct data including users, programmes, workouts, exercises, logs, and achievements.

---

## Running Tests

FitAct uses `pytest` with `pytest-flask` for automated testing. Tests run against an in-memory SQLite database to avoid affecting production data.

### Run all tests

```bash
pytest tests/ -v
```

### Run a specific test file

```bash
pytest tests/test_auth.py -v
```

---

## CI/CD Pipeline

FitAct uses a GitHub Actions CI/CD pipeline defined in `.github/workflows/ci-cd.yml`. The pipeline runs automatically on every push or pull request to the `main` branch.

### Pipeline Jobs

The pipeline consists of four sequential jobs:

**1. Test**
- Sets up Python 3.13
- Installs all dependencies from `requirements.txt`
- Initialises a SQLite test database
- Runs the Black code formatter check to enforce code style (NFR1)
- Runs the full pytest test suite

**2. SAST — CodeQL Security Scan**
- Runs in parallel with the Test job
- Uses GitHub's CodeQL action to perform static application security testing (SAST)
- Scans the Python codebase for known vulnerability patterns using the `security-extended` query set
- Results are uploaded to the GitHub Security tab (NFR4)

**3. Deliver**
- Only runs on pushes to `main` after both Test and SAST pass
- Builds a production-ready Docker image tagged with the commit SHA
- Pushes the image to GitHub Container Registry (GHCR)

**4. Deploy**
- Runs after Deliver completes
- Promotes the commit-tagged image to the `:latest` tag in GHCR
- The `:latest` image is what is used for local deployment and scaling (NFR6, NFR7)

### Pipeline Flow

```
Push to main
     │
     ├──── Test (Black + pytest) ────┐
     │                               ├──── Deliver (build + push to GHCR) ──── Deploy (:latest tag)
     └──── SAST (CodeQL) ────────────┘
```

---

## Extending FitAct

The following guidance is provided for developers looking to extend FitAct in future iterations.

### Adding a New Blueprint

1. Create a new folder under `app/` e.g. `app/nutrition/`
2. Add `__init__.py` (empty) and `routes.py` with a new Blueprint
3. Register the blueprint in `app/__init__.py` inside `create_app()`
4. Add corresponding templates under `templates/nutrition/`

### Adding a New Database Model

1. Define the new model class in `app/models.py`
2. Create a migration: `flask db migrate -m "add nutrition model"`
3. Apply the migration: `flask db upgrade`
4. If the model needs seed data, add it to `seed.py`

### Adding New Workout Programmes

All predefined programmes are seeded via `seed.py`. To add a new programme:

1. Add any new exercises to `exercises_data` in `seed.py`
2. Add the workout structure to `workouts_data`
3. Add the programme and its schedule to `programmes_data`
4. Run `python seed.py` to apply

### Adding New Achievement Badges

Achievements are defined in `seed.py` under `achievements_data` and awarded in `app/tracking/routes.py`. To add a new badge:

1. Add the achievement to `achievements_data` in `seed.py` and run the seeder
2. Add award logic in `app/tracking/routes.py` following the pattern of `award_first_workout_badge()`

### Extending the Password Policy

Password validation rules are centralised in `app/utils/validators.py`. Modify the `validate_password()` function and update the corresponding checklist in `templates/auth/register.html`.

### Extending the Firewall

Attack indicators are defined in `FIREWALL_INDICATORS` in `app/security/firewall.py`. New attack types and patterns can be added to the dictionary following the existing structure.

### Adding Tests

Add new test files to the `tests/` directory following the naming convention `test_<blueprint>.py`. Use the fixtures defined in `tests/conftest.py` for the app and client instances.