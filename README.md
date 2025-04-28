
# Realtime WebSocket Search for Companies

A Django Channels project providing **live search** functionality across companies and their related data models using **WebSockets**.

---

## Technologies Used

- Python 3.11.6
- Django 5.2
- Django Channels 4.2.2
- Daphne (ASGI server)
- SQLite3 (default dev database)
- WebsocketCommunicator (for unit testing WebSocket layers)

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/georgios48/realtime_django_search.git
cd realtime_django_search
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
DJANGO_SETTINGS_MODULE=realtime_search.settings
SECRET_KEY=your_secret_key
DEBUG=True
PYTHONPATH=.
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Run the Daphne server

Using the run_daphne.sh script, navigate to realtime_search, where manage.py is and execute:

```bash
./run_daphne.sh
```

Or run it manually:

```bash
daphne -b 127.0.0.1 -p 8000 realtime_search.asgi:application
```

---

## Running Tests

Navigate to realtime_search, where manage.py is located and run using:

```bash
python manage.py test
```
