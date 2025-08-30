# Django Backend Setup

## 1. Install Dependencies
pip install -r requirements.txt


## 2. Environment Setup
cp .env.example .env


## 3. Database Setup

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


## 4. Run Development Server

python manage.py runserver



## 5. API Endpoints
- Admin: http://127.0.0.1:8000/admin/
- API Docs: http://127.0.0.1:8000/api/docs/
- User Registration: POST /api/users/register/
- User Login: POST /api/users/login/
- Projects: /api/core/projects/
- Papers: /api/core/papers/

## 6. Integration with FastAPI
The Django backend is designed to communicate with FastAPI services running on port 8001.
