web: uvicorn config.asgi:application --host 0.0.0.0 --port 5000
broker: celery -A config.celery worker --loglevel=info
