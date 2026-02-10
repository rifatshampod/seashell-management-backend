# This document provides a guide for integrating the frontend with the backend.

## API Endpoints

### Authentication

- **Login**: `POST /api/v1/auth/login`
- **Logout**: `POST /api/v1/auth/logout`
- **Current User**: `GET /api/v1/auth/me`

### Seashells

- **Create Seashell**: `POST /api/v1/seashells/create`
- **List Seashells**: `GET /api/v1/seashells/`
- **Get Seashell**: `GET /api/v1/seashells/{seashell_id}`
- **Update Seashell**: `PUT /api/v1/seashells/{seashell_id}`
- **Delete Seashell**: `DELETE /api/v1/seashells/{seashell_id}`
- **Upload Image**: `POST /api/v1/seashells/{seashell_id}/upload-image`

### Filters

- **Species**: `GET /api/v1/seashells/filters/species`
- **Colors**: `GET /api/v1/seashells/filters/colors`
- **Conditions**: `GET /api/v1/seashells/filters/conditions`
- **Locations**: `GET /api/v1/seashells/filters/locations`

## Authentication

To authenticate with the backend, you need to send a Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

## File Uploads

To upload files, use the `multipart/form-data` content type.

## Example Requests

### Create Seashell

```http
POST /api/v1/seashells/create
Content-Type: multipart/form-data

name=Seashell&species=Shell&description=Shell&color=Red&size_mm=10&found_on=2022-01-01&found_at=Location&storage_location=Location&condition=Good&notes=Notes&file=file.jpg
```

### List Seashells

```http
GET /api/v1/seashells/
```

### Get Seashell

```http
GET /api/v1/seashells/{seashell_id}
```

### Update Seashell

```http
PUT /api/v1/seashells/{seashell_id}
Content-Type: multipart/form-data

name=Seashell&species=Shell&description=Shell&color=Red&size_mm=10&found_on=2022-01-01&found_at=Location&storage_location=Location&condition=Good&notes=Notes&file=file.jpg
```

### Delete Seashell

```http
DELETE /api/v1/seashells/{seashell_id}
```

### Upload Image

```http
POST /api/v1/seashells/{seashell_id}/upload-image
Content-Type: multipart/form-data

file=file.jpg
```

## Error Responses

```json
{
    "detail": "Error message"
}
```

## Notes

- All API endpoints require authentication.
- All API endpoints return JSON responses.
- All API endpoints use the same base URL: `http://localhost:8000`