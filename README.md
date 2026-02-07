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
scripts/          # Seed/admin helper scripts
```


## Table ideation:

1. `users`
2. `seashells`
3. `activity_log` (optional for now, will see if needed)

`users` table fields:
- id UUID PK
- email (unique, indexed)
- password_hash
- full_name optional/maybe not
- is_active bool
- created_at timestamp
- updated_at timestamp


`seashells` table fields:
- id UUID PRIMARY KEY DEFAULT gen_random_uuid()
- name VARCHAR(120) NOT NULL
- species VARCHAR(120) NOT NULL
- description TEXT NULL
- color VARCHAR(60) NULL
- size_mm INTEGER NULL CHECK (size_mm > 0)
- found_on DATE NULL
- found_at VARCHAR(200) NULL
- storage_location VARCHAR(150) NULL
- condition VARCHAR(50) NULL
- notes TEXT NULL
- image_url TEXT NULL
- created_at TIMESTAMPTZ NOT NULL DEFAULT now()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

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
