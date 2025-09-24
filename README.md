# Project Nexus – Job Board Platform

![Project Status](https://img.shields.io/badge/status-Completed-green)

## 🚀 Project Overview
**Jobboard** is a full-featured job listing and application platform built with Django. It allows users to browse, post, and apply for jobs. Admin users can manage users, job postings, and verification requests. only verified users can post a job. The project integrates with a remote PostgreSQL database for data persistence and is fully Dockerized for easy deployment.

---

## 📌 Features

### Core Features
- **User Registration & Authentication** – Sign up, login, and manage user accounts using JWT. 
- **Role Based Access control** - users and admins. 
- **Job Posting** – Employers(verified users) can create, update, and delete job listings.  
- **Job Application** – Authenticated users can apply to jobs with resume link and cover letter and track application status.
- **Application Management** - Employers can manage applications sent to their job by updating application status.
- **Browse Jobs** - any user can browse listed jobs

### Additional Features 
- **Notifications** – In-app and email notifications for job application updates using signals and background task for automation.  
- **Search & Filtering** – Quickly find relevant jobs by keywords, category, or status.
- **Account Verification** - Users can request verification and admins can verify users to enable them post jobs.
- **Extensive API documentation** - Interactive API documentation using Swagger.
- **Docker support** - For quick setup 

---

## 🛠 Technologies Used
- **Backend:** Django, Django REST Framework, Celery  
- **Database:** PostgreSQL  
- **Frontend:** None (API-focused)  
- **Tools:** Postman (API testing), Git(version control), Docker(containerization), ERD Tool (dbdiagram.io), Pythonanywhere (deployment)

---

## 📁 Database Models
- **User:** Stores user information, roles, and authentication details.  
- **Job:** Represents job listings with title, description, category, and owner.  
- **Application:** Tracks which users have applied for which jobs and their application status.  
- **Category:** Organizes jobs into categories for easier browsing.  
- **Notification:** Handles in-app and email notifications for users.
- **Verification Request** Represent user request for account verification.

**Note** - For detailed DB specification refer to our DB_schema.md file.

---

## ⚡ Setup Instructions
### Manual Setup(without docker)
**Prerequisites**:
   - Python 3.12
   - PostgreSQL database (remote or local)
   - Git

1. Clone the repository:
   ```bash
   git clone https://github.com/Menwuyelet/jobboard
   cd jobboard
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Configure db:
   - in jobboard/settings.py:
   ```bash
      DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'your_db_host',
            'PORT': 'your_db_port',
         }
      }
   ```
   ```bash
   python manage.py migrate
   python manage.py runserver
   celery -A jobboard worker -l info
   ```
   **Note** - To setup own db, celery worker, and email provider edit the settings.py and follow the same instruction or add .env file with all variables.
5. Open in your browser: http://localhost:8000

### Docker Setup(Recommended)
**Prerequisites**:
   - Docker
   - Docker Compose
   - .env file with your database and environment variables(or hard code them in settings.py)

1. Clone the repository:
   ```bash
   git clone https://github.com/Menwuyelet/jobboard
   cd jobboard
   ```
2. Build the Docker image:
   ```bash
   docker-compose build
   ```
3. Run the container:
   ```bash
   docker-compose up
   docker-compose exec web python manage.py migrate (for migrating db after containers are up)
   ```
   **Note** - To setup own db, celery worker, and email provider edit the settings.py and follow the same instruction or add .env file with all variables.
4. Access the app: http://localhost:8000

## User Interaction Guide
### For Regular Users
   - Any user can list all the jobs and browse them.
   - To apply for a job user must be authenticated.
   - To post a job user must be verified.
   - To verify user use the user verification url to send request to Admin user after authentication.
   - After successful Verification a user can post jobs and manage applications to that job using the endpoints provided.

### Admin cred:
   ```bash
   email: admin@gmail.com
   PW: admin@21
   ```


**Note** - Use the ```api/docs``` url or click the link on landing page to access the extensive API doc.

### For questions or feedback, contact: *Mnu Temesgen* at *menutemesgen@gmail.com*
