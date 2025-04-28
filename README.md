
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

## Testing

### Manual testing
Inside manual_testing_utils, you can find an existing database with 2 existing test models.
There is also an existing superuser created: with credentials "admin" for username and "admin" for password.

Replace the original database inside realtime_search with the test sampled one inside manual_testing_utils.

After that you can use postman in order to send queries. The user input is stored inside the "query" property of the JSON body, in other words:

After running daphe, connect to the WebSocket address -> ws://localhost:8000/ws/search/

And send messages using this template:

```
{
    "query": "<userInput>"
}
```

Unable to provide exported postman collection due to issue in exporting postman collections that include websocket

### Running unittests
Navigate to realtime_search, where manage.py is located and run using:

```bash
python manage.py test
```
