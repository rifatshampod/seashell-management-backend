# Seashell Management Backend (kone-cloud-developer-trainee-assignment)

> Repository of technical assessment project for KONE summer trainee (Cloud Developer) position. Please refrain from using this for personal or professional use. This repository will be archived after the recruitment process is completed. 

Overview

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (Bearer Token)
- **Deployment**: Docker Compose

Features

## Project Structure
Directory Structure:
```bash
app/
  api/            # Versioned API endpoints
  core/           # Config, security, OpenAPI setup
  db/             # Models, session, repositories
  schemas/        # Request/response validation
  services/       # Business logic
alembic/          # Database migrations
scripts/          # Seed helper scripts
documentation/    # Documentation resources with front end instructions
uploads/          # Uploaded seashell images
```

Backend Architecture:

[![Backend Architecture](documentation/seashell-erd-backend-architecture.drawio.png)](documentation/seashell-erd-backend-architecture.drawio.png)

## Quick Start (Setup Instructions)

### 0. Prerequisites

Install the following before proceeding:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Docker Desktop | Latest | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |

## Database Structure

1. `users` table
2. `seashells` table

[![Seashell ER Diagram](documentation/seashell-erd.drawio.png)](documentation/seashell-erd.drawio.png)

### 1. Clone Repository

```bash
git clone https://github.com/rifatshampod/seashell-management-backend.git
cd seashell-management-backend
```

### 2. Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

The dependencies are listed in the `requirements.txt` file. Install them using pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Use the `.env.example` file as a template and rename it to `.env` (to make this tech assessment easier, the values in `.env.example` are already set):

```bash
cp .env.example .env
```

### 5. Start PostgreSQL Database

```bash
docker-compose up -d
```

Verify database is running:
```bash
docker ps
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Seed Initial Data

```bash
python scripts/seed.py
```

**Default Test User:**
- Email: `test@seashell.com`
- Password: `password123`

### 8. Start Development Server

```bash
uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**


## API Documentation

## Frontend Integration
<!-- 
## Design Notes -->


## Important Functionalities

**Authentication:**
- Login (email + password)
- Logout
- Current user info (to show the user name/email in the UI and confirm session)

**User Management:**
- Seed initial users (one-time: create first user(s) by migration/CLI/admin page)
- Create new user
- List users
- Activate/Deactivate user (instead of deleting users)
- Reset user password

**Seashell Management:**
- Add seashell
- Edit seashell
- Delete seashell
- View seashell list
- View seashell details

**Interactions:**
- Search (by name/species/description—one search box)
- Filter by species (dropdown)
- Sort (newest/oldest, name A–Z) (lets see if needed)
- Pagination (simple next/prev) (lets see if needed)

