# kone-cloud-developer-trainee-assignment

> Repository of technical assessment project for KONE summer trainee (Cloud Developer) position. Please refrain from using this for personal or professional use. This repository will be archived after the recruitment process is completed. 

## Project Stucture
```bash
app/
  api/            # Versioned API endpoints
  core/           # Config, security, OpenAPI setup
  db/             # Models, session, repositories
  schemas/        # Request/response validation
  services/       # Business logic
alembic/          # Database migrations
tests/            # Automated tests
scripts/          # Seed helper scripts
```


## Table ideation:

1. `users` table
2. `seashells` table

[![Seashell ER Diagram](documentation/seashell-erd.drawio.png)](documentation/seashell-erd.drawio.png)


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

> mmmmm, so far this..... some might not be needed
