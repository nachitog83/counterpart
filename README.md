## The Challenge

We're going to create a system that will use the **USGS Earthquake** public data set to show us where the nearest earthquake above a 5.0 was in relation to one of the following cities, between 2 dates that the user specifies:
1. Los Angeles, CA
2. San Francisco, CA
3. Tokyo, Japan

The result returned should show something like:

**Result for Los Angeles between June 1 2021 and July 5 2021 : The closest Earthquake to Los Angeles was a M 5.7 - South of Africa on June 30**

The application should also save the results every time we run the search in some database, and allow us to view the results again as quickly as possible.
If no results were found during those dates, simply show a **“No results found”**.

#### The system will consist of the following:

1. An endpoint to create a new city
2. An endpoint for us to search for earthquakes
	1. Including
		1. A start date for the search
		2. An end date for the search
	2. A results JSON of current results of the search

## Resolution

#### Introduction

For this challenge, the approach was to create a simple, yet efficient Django app to store cities and retrieve their closest earthquakes.

To design this app, I followed a Repository Pattern (which, to be honest, I'm a big fan of).

Essentially, it provides an abstraction of data, so that your application can work with a simple abstraction that has an interface approximating that of a collection. Adding, removing, updating, and selecting items from this collection is done through a series of straightforward methods, without the need to deal with database concerns like connections, commands, cursors, or readers. Using this pattern can help achieve loose coupling and can keep domain objects persistence ignorant.

This Repository pattern is a simplifying abstraction over data storage, allowing us to decouple our model layer from the data layer, reduce code duplication, among other pros.

#### Code Structure

```
.
├── app
│   ├── asgi.py
│   ├── __init__.py
│   ├── repositories.py
│   ├── settings.py
│   ├── static
│   ├── storage.py
│   ├── urls.py
│   └── wsgi.py
├── cities
│   ├── admin.py
│   ├── apps.py
│   ├── cassettes
│   │   └── test_get_city_coords.yaml
│   ├── dataclasses.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── repository.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── earthquakes
│   ├── admin.py
│   ├── apps.py
│   ├── cassettes
│   │   ├── test_usgs_client_fail.yaml
│   │   └── test_usgs_client_sucesss.yaml
│   ├── clients.py
│   ├── dataclasses.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── repository.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── gunicorn.cfg.py
├── manage.py
├── pytest.ini
├── requirements.txt
└── static

```

#### Infrastructure

##### Database

1. PostgresSQL: to store City and Earthquake data.
2. Redis: Cache for storing queries to USGS database.

##### Framework

Django with Django REST to handle API views (in this case I chose not to use serializers to avoid bloating the code too much).

App is handled with gunicorn.

##### Application

Application is containerized with docker and docker compose.

To install and run application, run the following command: `docker-compose up --build` from the source directory where files where uncompressed.

Once running, attach to docker container with `docker exec -it django-app bash` and run:
1. `python manage.py makemigrations`
2. `python manage.py migrate`
3. `python manage.py createsuperuser` (optional)

Once up and running, use the follow queries:

*Cities:*

1. Create City:
```bash
curl --location --request POST 'http://127.0.0.1:8000/v1/cities/create/' \
--header 'Content-Type: application/json' \
--data-raw '{
"name": "Los Angeles",
"state": "California",
"country": "US"
}'
```

2. Get all Cities:
```bash
curl --location --request GET 'http://127.0.0.1:8000/v1/cities/get/'
```

3. Get City by index:
```bash
curl --location --request GET 'http://127.0.0.1:8000/v1/cities/get/1/'
```

*Earthquakes*

1. Get closest earthquake:
```bash
curl --location --request POST 'http://127.0.0.1:8000/v1/earthquakes/get_closest/' \
--header 'Content-Type: application/json' \
--data-raw '{
"start_time": "2021-06-07",
"end_time": "2021-07-07"
}'
```

##### Testing

Test suite was created with pytest.

To run the test suite: `docker exec -it django-app pytest -s -v . --cov `

*Results*

```
===================================================================================== test session starts ====================================================================================
platform linux -- Python 3.10.8, pytest-7.1.3, pluggy-1.0.0 -- /usr/local/bin/python
cachedir: .pytest_cache
django: settings: app.settings (from ini)
rootdir: /src, configfile: pytest.ini
plugins: cov-4.0.0, django-4.5.2, vcr-1.0.2
collected 22 items                                                                                                                                                                                                

cities/tests.py::test_city_handler_create Creating test database for alias 'default'...
PASSED
cities/tests.py::test_get_all_cities_view PASSED
cities/tests.py::test_get_one_cities_view PASSED
earthquakes/tests.py::test_get_from_db PASSED
earthquakes/tests.py::test_save_new_closest_earthquake PASSED
earthquakes/tests.py::test_add_new_closest_earthquake_for_city PASSED
earthquakes/tests.py::test_execute_with_saved_obj PASSED
earthquakes/tests.py::test_execute_without_saved_obj PASSED
cities/tests.py::test_create_city_dto[False-kwargs0] PASSED
cities/tests.py::test_create_city_dto[True-kwargs1] PASSED
cities/tests.py::test_create_city_dto[True-kwargs2] PASSED
cities/tests.py::test_create_city_dto[True-kwargs3] PASSED
cities/tests.py::test_get_city_coords PASSED
cities/tests.py::test_city_create_view_success[201-kwargs0] PASSED
cities/tests.py::test_city_create_view_success[400-kwargs1] PASSED
cities/tests.py::test_city_create_view_success[400-kwargs2] PASSED
earthquakes/tests.py::test_usgs_client_sucesss PASSED
earthquakes/tests.py::test_usgs_client_fail PASSED
earthquakes/tests.py::test_get_closest_earthquake PASSED
earthquakes/tests.py::test_city_create_view_success[200-kwargs0] PASSED
earthquakes/tests.py::test_city_create_view_success[400-kwargs1] PASSED
earthquakes/tests.py::test_city_create_view_not_found PASSEDDestroying test database for alias 'default'...
```

*Coverage*

```
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
app/__init__.py                              0      0   100%
app/repositories.py                         35      4    89%
app/settings.py                             27      0   100%
app/storage.py                               3      0   100%
app/urls.py                                  3      0   100%
cities/__init__.py                           0      0   100%
cities/admin.py                              3      0   100%
cities/apps.py                               4      0   100%
cities/dataclasses.py                       14      0   100%
cities/migrations/0001_initial.py            5      0   100%
cities/migrations/__init__.py                0      0   100%
cities/models.py                            10      1    90%
cities/repository.py                         6      0   100%
cities/services.py                          25      1    96%
cities/tests.py                             53      0   100%
cities/urls.py                               3      0   100%
cities/views.py                             30      2    93%
earthquakes/__init__.py                      0      0   100%
earthquakes/admin.py                         3      0   100%
earthquakes/apps.py                          4      0   100%
earthquakes/clients.py                      25      4    84%
earthquakes/dataclasses.py                  21      0   100%
earthquakes/migrations/0001_initial.py       6      0   100%
earthquakes/migrations/__init__.py           0      0   100%
earthquakes/models.py                       13      2    85%
earthquakes/repository.py                    6      0   100%
earthquakes/services.py                     43      1    98%
earthquakes/tests.py                        80      0   100%
earthquakes/urls.py                          3      0   100%
earthquakes/views.py                        30      5    83%
------------------------------------------------------------
TOTAL                                      455     20    96%
```
