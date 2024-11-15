SpamLookupify

Note: For a cleaner version, please refer to the README PDF. Follow the text-labeled instructions and run commands in your terminal.

1. Overview
   This project is a Django-based application that allows users to manage contacts, report spam numbers, and search for contacts by names and phone numbers. It features user registration, login, and a global search functionality.

2. Features
   - User registration and login
   - Manage contacts (create, read, update, delete)
   - Report spam contacts
   - Search contacts by name or phone number
   - View contact details with spam likelihood
   - rate limit available (Uncomment throttle classes in views.py to add rate limit)

3. Requirements
   - Python 3.8 or higher
   - Django 3.2 or higher
   - Django REST Framework
   - PostgreSQL or any supported database

4. Getting Started
   Step 1: Download and Extract
      1. Download the project ZIP file from the provided source.
      2. Extract the contents to your desired location.

   Step 2: Setup the Environment
      A. Create a virtual environment:
         Command: python -m venv .venv

      B. Activate the virtual environment:
         - On Windows: .venv\Scripts\activate
         - On macOS/Linux: source .venv/bin/activate

      C. Install required packages:
         Command: pip install -r requirements.txt

   Step 3: Configure Database
      1. For default SQLite, leave `settings.py` as is.
      2. To use a different database (e.g., PostgreSQL, MySQL), update the database settings in settings.py to match your database configuration.
         Note: check the README PDF for step 2

      3. After configuring, run:
         Command: python manage.py makemigrations
         Command: python manage.py migrate
         
   Step 3.1: Generate Test Data
      1. populate_db.py script in SpamLookupify/management/commands helps to populate test data
         Command: python manage.py populate_db

   Step 4: Create a Superuser (Optional)
      Command: python manage.py createsuperuser

   Step 5: Run the Development Server
      Command: python manage.py runserver
      Open your browser at http://127.0.0.1:8000/ to access the application.

   Step 6: Testing:
      1. Through Test file:
         Command: python manage.py test

      2. Through Postman:

Important: 1. for first time setup please hit login api after register api to generate csrftoken and sessionid

API Endpoints (Test using Postman):
   User Authentication:
      - Register User
         - URL: /api/register/
         - Method: POST
         - Body:
         {
             "name": "string",
             "username": "string",
             "password": "string",
             "phone_number": "string",
             "email": "string" (optional)
         }

      - Login User
         - URL: /api/login/
         - Method: POST
         - Body:
         {
             "username": "string",
             "password": "string"
         }
      
      - Logout
         - URL: /api/logout/
         - Method: POST

   Contacts Management:
      - List/Create Contacts
         - URL: /api/contacts/
         - Method: GET / POST
         - Body (for POST):
         {
             "name": "string",
             "phone_number": "string"
         }

      - Retrieve/Update/Delete Contact
         - URL: /api/contacts/<id>/
         - Method: GET / PUT / DELETE

   Spam Reporting:
      - Report Spam
         - URL: /api/report-spam/
         - Method: POST
         - Body:
         {
             "phone_number": "string"
         }

   Search Functionality:
      - Search Contacts by Name
         - URL: /api/search/
         - Method: GET
         - Query Parameters:
            - query: string

      - Search Contacts by Phone Number
         - URL: /api/search/
         - Method: GET
         - Query Parameters:
            - phone_number: string
