## Weather Forecast App (Poor Man's Gismeteo)

### Prerequisites

- Python 3.10+
- Django 5
- jQuery
- Docker

### Description

This is a Django-based web application for checking the weather forecast. Users can search for weather forecasts by city and see detailed information about the weather. The application also provides autocomplete suggestions for city names and remembers the last searched city for the user's convenience.

### Features

- Search for weather forecasts by city
- Autocomplete suggestions for city names
- Displays detailed weather information including temperature, precipitation, wind speed, and weather description
- Remembers the last searched city using cookies
- Supports city names in Russian and any language

### Running
After clonning these repo use these simple Docker commands:

<u>docker build -t my_django_app .</u>         - build image in Docker 

<u>docker run -p 8000:8000 my_django_app</u>         - run docker image with app using port 8000 

Check the weather on localhost:8000

### Testing
Running tests:

<u>python manage.py test</u>

