### Prerequisites

- Python (3.8 or higher)
- pip (Python package installer)
- Git

### Steps

1. clone or download the code from Github  
    ```
    git clone https://github.com/nanokwok/ku-polls.git
    ```  
2. change directory to the project root  
    ```
    cd ku-polls
    ```
3. Create virtual environment
    ```
    python -m venv venv
    ```
4. Activate virtual environment
   - On MacOS or Linux:
     ```
     . venv/bin/activate
     ```
   - On Windows:
     ```
     .venv\Scripts\activate.bat
     ```
5. install dependencies  
    ```
    pip install -r requirements.txt
    ```
6. Set Up the Secret Key (For Development)
   - Create a file named `.env` in the same directory as `manage.py`:
   - If you don't have a SECRET_KEY, you can set one up temporarily using:
     ```
     from django.core.management.utils import get_random_secret_key
     print(get_random_secret_key())
     ```
   - On Linux/MacOS:
     ```
     cp sample.env .env
     ```
   - On Windows:
     ```
     copy sample.env .env
     ```
7. Run migrations  
    ```
    python manage.py migrate
    ```
8. Load initial data
    ```
    python manage.py loaddata data/polls-v4.json
    ```
9. run server
    ```
    python manage.py runserver
    ```
    if css seem not correct
    ```
    python manage.py runserver --insecure
    ```