# Django Event Management System

A web-based event management system built with Django, allowing admins, faculty, and students to manage and participate in events.

## How to Set Up on Windows

1. Download or clone the project:
   - Download the ZIP and extract it
   - Or clone using: `git clone https://github.com/UK-71/Event-Management.git`

2. Navigate to the project directory:
   - `cd django-event-management-master`

3. Create a virtual environment:
   - `python -m venv myenv`

4. Activate the virtual environment:
   - `myenv\Scripts\activate`

5. Install required packages:
   - `pip install -r requirements.txt`

6. Apply database migrations:
   - `python manage.py migrate`

7. Create a superuser:
   - `python manage.py createsuperuser`

8. Run the development server:
   - `python manage.py runserver`

9. Access the application at:
   - `http://127.0.0.1:8000/`

## Features

- Multi-role support: Admin, Faculty, and Student
- Event creation and registration
- Attendance tracking
- Feedback system
- Favorite/wishlist events
- Dashboard for each user role
- Modular structure using Django apps



