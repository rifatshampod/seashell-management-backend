# kone-cloud-developer-trainee-assignment

>> Repository of technical assessment project for KONE summer trainee (Cloud Developer) position. Please refrain from using this for personal or professional use. This repository will be archived after the recruitment process is completed. 

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
