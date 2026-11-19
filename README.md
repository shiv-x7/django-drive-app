# Cloud Drive – Django File Storage Application

A Google Drive-inspired cloud storage application built using Python and Django. It allows users to securely upload, organize, search, view, and download their files.

## Features

- User Registration and Authentication
- Secure File Upload and Download
- File Preview
- Create, Rename and Delete Folders
- Move Files Between Folders
- File and Folder Search
- Storage Usage Dashboard
- 500 MiB Storage Limit per User
- 25 MiB Individual File Upload Limit
- User-specific File Access
- Responsive Dashboard Interface

## Technology Stack

- Backend: Python, Django
- Database: SQLite (current development configuration)
- Frontend: HTML, CSS, Bootstrap, JavaScript
- Icons: Bootstrap Icons
- Version Control: Git and GitHub

## Project Structure

```text
cloud_drive/
├── accounts/
├── api/
├── core/
├── drive/
├── cloud_drive/
├── templates/
│   ├── accounts/
│   └── drive/
├── manage.py
└── .gitignore
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/shiv-x7/django-drive-app.git
```

2. Navigate to the project directory:

```bash
cd django-drive-app
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the environment on Windows:

```bash
venv\Scripts\activate
```

5. Install project dependencies.

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

6. Apply migrations:

```bash
python manage.py migrate
```

7. Start the development server:

```bash
python manage.py runserver
```

8. Open the application:

```text
http://127.0.0.1:8000/
```

## Future Improvements

- PostgreSQL Database Integration
- Cloud Storage Integration
- Production Deployment
- Advanced File Management

## Author

Shivank sirotia

GitHub: https://github.com/shiv-x7