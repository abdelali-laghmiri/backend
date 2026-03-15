# Project Backend Summary

## Section 1 - System Overview

This backend is an HR management platform built with FastAPI, SQLAlchemy, Alembic, and JWT authentication.

It supports:

- user authentication and password management
- organization structure management
- employee management
- database-driven permissions
- attendance check-in and check-out
- request submission and approval workflows
- admin and user dashboard data

The codebase follows a modular `apps/` structure. Each module generally contains:

- `models.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic request and response schemas
- `services.py`: business logic
- `routers.py`: FastAPI endpoints

The API publishes OpenAPI documentation through:

- `/docs`
- `/openapi.json`


## Section 2 - Main Modules

### auth

Responsible for:

- login
- JWT token issuance
- current user retrieval
- password changes
- first-login password reset flow

Key endpoints:

- `POST /auth/login`
- `POST /auth/change-password`
- `GET /auth/me`

### organization

Responsible for:

- job titles
- departments
- teams

Key ideas:

- employees belong to a job title
- teams belong to departments
- job titles participate in permissions and approval workflows

### employees

Responsible for:

- creating user accounts and employee profiles together
- employee listing and profile retrieval
- employee updates and safe deletion rules

Key ideas:

- employee creation also creates a `User`
- employee records link to department, team, and job title
- a temporary password may be returned on creation

### permissions

Responsible for:

- storing permissions in the database
- assigning permissions to job titles
- protecting endpoints through permission checks

Key ideas:

- permissions live in the `permissions` table
- assignments live in `job_title_permissions`
- superusers bypass permission checks

### attendance

Responsible for:

- employee check-in
- employee check-out
- attendance history

Key ideas:

- only one open attendance record is allowed per employee
- check-out must happen after check-in

### requests

Responsible for:

- request type configuration
- dynamic request fields
- approval workflow setup
- employee request creation
- approval and rejection history

Key ideas:

- request forms are dynamic
- workflows are based on approval steps stored in the database
- approval comments and history are persisted

### dashboard

Responsible for:

- admin dashboard statistics
- admin attendance summary
- admin request summary
- personal user dashboard summary


## Section 3 - Authentication

The backend uses JWT bearer authentication.

### Login flow

Endpoint:

- `POST /auth/login`

Request type:

- `application/x-www-form-urlencoded`

Frontend sends:

- `username`: user matricule
- `password`: user password

Example response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "requires_password_change": true,
  "message": "Password change required before normal use."
}
```

### Using the token

Protected endpoints require:

```http
Authorization: Bearer <token>
```

Common headers for authenticated JSON requests:

```http
Authorization: Bearer <token>
Content-Type: application/json
Accept: application/json
```

### First login flow

If `requires_password_change` is `true`:

1. Store the token.
2. Redirect the user to a password change screen.
3. Call `POST /auth/change-password`.
4. Refresh user state with `GET /auth/me`.


## Section 4 - API Architecture

### Auth

- `POST /auth/login`
- `POST /auth/change-password`
- `GET /auth/me`

Purpose:

- login and token retrieval
- password change
- current user bootstrap for the frontend

### Organization

- `POST /organization/job-titles`
- `GET /organization/job-titles`
- `DELETE /organization/job-titles/{job_title_id}`
- `POST /organization/departments`
- `GET /organization/departments`
- `DELETE /organization/departments/{department_id}`
- `POST /organization/teams`
- `GET /organization/teams`
- `DELETE /organization/teams/{team_id}`
- `GET /organization/departments/{department_id}/teams`

Purpose:

- manage company structure
- load reference data for employee forms and dashboards

### Employees

- `POST /employees/`
- `GET /employees/`
- `GET /employees/me/profile`
- `GET /employees/{employee_id}`
- `PUT /employees/{employee_id}`
- `DELETE /employees/{employee_id}`

Purpose:

- manage employee records
- load current employee profile
- power employee management screens

### Permissions

- `GET /permissions/`
- `POST /permissions/`
- `DELETE /permissions/{permission_id}`
- `GET /permissions/job-titles/{job_title_id}`
- `POST /permissions/job-titles/{job_title_id}`
- `DELETE /permissions/job-titles/{job_title_id}/{permission_id}`

Purpose:

- manage system permissions
- assign permissions to job titles

### Attendance

- `POST /attendance/check-in`
- `POST /attendance/check-out`
- `GET /attendance/me`
- `GET /attendance/employee/{employee_id}`

Purpose:

- record attendance punches
- expose employee attendance history

### Requests

- `POST /requests/`
- `GET /requests/my`
- `GET /requests/approvals`
- `GET /requests/{request_id}`
- `POST /requests/{request_id}/approve`
- `POST /requests/{request_id}/reject`
- `GET /requests/types`
- `POST /requests/types`
- `GET /requests/types/{type_id}/fields`
- `POST /requests/types/{type_id}/fields`
- `PUT /requests/fields/{field_id}`
- `DELETE /requests/fields/{field_id}`
- `GET /requests/types/{type_id}/form`
- `GET /requests/types/{type_id}/steps`
- `POST /requests/steps`

Purpose:

- configure request types and workflows
- submit employee requests
- process approvals

### Dashboard

- `GET /admin/dashboard/stats`
- `GET /admin/dashboard/attendance-summary`
- `GET /admin/dashboard/request-summary`
- `GET /dashboard/me/summary`

Purpose:

- load admin dashboards
- load personal user dashboard data


## Section 5 - Frontend Integration Guide

### Base URL

Examples:

- local: `http://localhost:8000`
- production: `https://your-backend-domain`

### OpenAPI

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

The OpenAPI spec currently exposes 38 paths and uses `OAuth2PasswordBearer` with `tokenUrl: "auth/login"`.

### CORS

The backend allows requests from the configured `FRONTEND_URL`.

Default:

```env
FRONTEND_URL=http://localhost:3000
```

For deployment:

```env
FRONTEND_URL=https://your-frontend-domain
```

If multiple frontend origins are needed in the same environment, `FRONTEND_URL` can be a comma-separated list.

### Authentication flow

1. Call `POST /auth/login` with form data.
2. Save the `access_token`.
3. Send `Authorization: Bearer <token>` on protected requests.
4. If `requires_password_change` is `true`, call `POST /auth/change-password`.
5. Load the current user with `GET /auth/me`.

### Example API calls

Login with `fetch`:

```js
const body = new URLSearchParams({
  username: matricule,
  password,
});

const response = await fetch(`${BASE_URL}/auth/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body,
});
```

Authenticated request:

```js
const response = await fetch(`${BASE_URL}/employees/`, {
  headers: {
    Authorization: `Bearer ${token}`,
    Accept: "application/json",
  },
});
```

### Pagination

Several list endpoints support:

- `limit`
- `offset`

Example:

```http
GET /employees/?limit=20&offset=0
```

Current behavior:

- list responses remain plain arrays
- there is no `{ items, total }` response envelope


## Section 6 - Example Frontend Flow

### 1. Login

1. Send credentials to `POST /auth/login`.
2. Store the access token.
3. If required, force a password change with `POST /auth/change-password`.
4. Fetch `GET /auth/me`.

### 2. Load dashboard

Admin UI:

- `GET /admin/dashboard/stats`
- `GET /admin/dashboard/attendance-summary`
- `GET /admin/dashboard/request-summary`

Employee UI:

- `GET /dashboard/me/summary`

### 3. Fetch employees

- `GET /employees/?limit=20&offset=0`

Typical frontend usage:

- show list pages
- open employee details
- edit employee profile assignments

### 4. Submit a request

1. Load request types with `GET /requests/types`.
2. Load the dynamic form definition with `GET /requests/types/{type_id}/form`.
3. Build the form dynamically in the frontend.
4. Submit the request with `POST /requests/`.

### 5. Approve requests

1. Load pending approvals with `GET /requests/approvals`.
2. Load full request details with `GET /requests/{request_id}`.
3. Approve or reject with:
   - `POST /requests/{request_id}/approve`
   - `POST /requests/{request_id}/reject`


## Section 7 - Data Flow

### Frontend -> API -> Database

Typical request flow:

1. The frontend sends an HTTP request to a FastAPI router.
2. The router validates the payload with a Pydantic schema.
3. The router delegates work to a service function.
4. The service queries or updates SQLAlchemy models.
5. SQLAlchemy persists data to PostgreSQL.
6. The router serializes the response with a schema.
7. The frontend receives JSON.

Example for request creation:

1. Frontend sends `POST /requests/`.
2. Backend validates the request type and employee.
3. Backend creates the request and initial workflow state.
4. Backend returns the created request as JSON.


## Section 8 - Security

### Role system

Global user roles:

- `user`
- `superuser`

Superusers bypass permission checks.

### Permission system

Permissions are database-driven.

Flow:

1. Permissions are stored in `permissions`.
2. Assignments are stored in `job_title_permissions`.
3. Employees inherit permissions through their job title.
4. Endpoints can enforce access through `require_permission("permission_name")`.

### Job title permissions

Permissions are not assigned directly to users.

Instead:

- employee -> job title -> permissions

This is important for frontend admin screens because permission management should happen at the job title level.

### Active user checks

The backend enforces active-user validation:

- inactive users cannot log in
- inactive users cannot access protected endpoints with old tokens


## Section 9 - Important API Endpoints

### Authentication

- `POST /auth/login`
- `POST /auth/change-password`
- `GET /auth/me`

### Dashboard

- `GET /dashboard/me/summary`
- `GET /admin/dashboard/stats`

### Employees

- `GET /employees/`
- `POST /employees/`
- `GET /employees/me/profile`

### Organization

- `GET /organization/job-titles`
- `GET /organization/departments`
- `GET /organization/teams`

### Permissions

- `GET /permissions/`
- `GET /permissions/job-titles/{job_title_id}`
- `POST /permissions/job-titles/{job_title_id}`

### Attendance

- `POST /attendance/check-in`
- `POST /attendance/check-out`
- `GET /attendance/me`

### Requests

- `GET /requests/types`
- `GET /requests/types/{type_id}/form`
- `POST /requests/`
- `GET /requests/my`
- `GET /requests/approvals`
- `GET /requests/{request_id}`
- `POST /requests/{request_id}/approve`
- `POST /requests/{request_id}/reject`


## Section 10 - Example Requests

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=change_me
```

Example response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "requires_password_change": true,
  "message": "Password change required before normal use."
}
```

### Change password

```json
{
  "old_password": "change_me",
  "new_password": "AdminPassword1!"
}
```

### Create employee

```json
{
  "matricule": "emp001",
  "first_name": "Eli",
  "last_name": "Employee",
  "email": "employee@example.com",
  "phone": "5550001234",
  "hire_date": "2026-03-02",
  "department_id": 1,
  "team_id": 1,
  "job_title_id": 2,
  "initial_password": null
}
```

Example response:

```json
{
  "id": 2,
  "user_id": 3,
  "first_name": "Eli",
  "last_name": "Employee",
  "email": "employee@example.com",
  "phone": "5550001234",
  "hire_date": "2026-03-02",
  "department_id": 1,
  "team_id": 1,
  "job_title_id": 2,
  "current_leave_balance": 0,
  "employment_status": "ACTIVE",
  "temporary_password": "generated-temporary-password"
}
```

### Create request

```json
{
  "request_type_id": 1,
  "extra_data": {
    "start_date": "2026-04-01",
    "end_date": "2026-04-05",
    "reason": "Annual leave"
  }
}
```

### Approve request

```json
{
  "comment": "Approved by manager"
}
```

### Assign permission to job title

```json
{
  "permission_id": 3
}
```

### User dashboard example

```json
{
  "employee_id": 2,
  "has_open_attendance": false,
  "pending_requests": 1,
  "pending_approvals": 0,
  "recent_requests": [
    {
      "id": 10,
      "request_type_name": "Leave Request",
      "status": "PENDING",
      "created_at": "2026-03-15T10:00:00Z"
    }
  ],
  "notifications": [
    {
      "level": "info",
      "message": "You have 1 pending request(s)."
    }
  ]
}
```


## Notes for Frontend Developers

- `POST /auth/login` uses form data, not JSON.
- Most protected endpoints require `Authorization: Bearer <token>`.
- Many list endpoints support `limit` and `offset`.
- Request forms are dynamic, so the frontend should build request UIs from `/requests/types/{type_id}/form`.
- Employee creation may return a temporary password. Admin UIs should display it once and communicate it securely.
- `/openapi.json` can be used for client generation.
