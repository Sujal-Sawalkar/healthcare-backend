# Healthcare Backend (Django + DRF + PostgreSQL + JWT)

## Setup
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then edit values
# create the DB first:  psql -U postgres -c "CREATE DATABASE healthcare_db;"
python manage.py migrate
python manage.py runserver
```
Run tests: `python manage.py test tests`

## Endpoints
| Method | URL | Notes |
|---|---|---|
| POST | /api/auth/register/ | `{name, email, password}` |
| POST | /api/auth/login/ | `{email, password}` -> `access`, `refresh` |
| POST | /api/auth/token/refresh/ | `{refresh}` (bonus) |
| POST/GET | /api/patients/ | GET = only your patients |
| GET/PUT/DELETE | /api/patients/<id>/ | only your patients |
| POST/GET | /api/doctors/ | GET = all doctors |
| GET/PUT/DELETE | /api/doctors/<id>/ | edit/delete: creator only |
| POST/GET | /api/mappings/ | `{patient, doctor}`; GET = mappings of your patients |
| GET | /api/mappings/<patient_id>/ | doctors assigned to that patient |
| DELETE | /api/mappings/<id>/ | remove a mapping |

Send `Authorization: Bearer <access>` on everything except register/login.

## Postman quick flow
1. Register -> Login, copy `access`.
2. Postman: Authorization tab -> Bearer Token -> paste.
3. POST /api/patients/ `{"name":"Ravi","age":40,"gender":"M","phone":"9876543210"}`
4. POST /api/doctors/ `{"name":"Meera","specialization":"Cardiology","email":"meera@hospital.com","experience_years":8}`
5. POST /api/mappings/ `{"patient":1,"doctor":1}`
6. GET /api/mappings/1/ (patient 1's doctors) -> DELETE /api/mappings/<mapping id>/
