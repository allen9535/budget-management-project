python manage.py makemigrations
python manage.py migrate
gunicorn main.wsgi:application --bind 0.0.0.0:8000