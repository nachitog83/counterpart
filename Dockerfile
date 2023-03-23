FROM python:3.10-slim-buster


# Install Debian packages
RUN apt-get -qq update && apt-get -qq -y install python3-pip \
    python-psycopg2 \
    postgresql-server-dev-all \
    python3-dev \
    python-gdal \
    python-geoip \
    postgresql-client

ARG SECRET_KEY
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 0

RUN mkdir -p /src
WORKDIR /src

# Install Django and libraries
COPY ./src /src
RUN pip install --upgrade pip
RUN set ex && pip install -r /src/requirements.txt
RUN apt-get -qq -y autoremove && apt-get autoclean

# copy entrypoint-prod.sh
COPY ./entrypoint.sh /src
RUN python manage.py collectstatic --no-input

# Clean up
RUN apt-get -qq -y autoremove \
    && apt-get autoclean
