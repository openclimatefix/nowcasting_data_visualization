FROM python:3.9-slim-buster

# copy files over
COPY ./application /app/application
COPY ./tests /app/tests
COPY ./requirements.txt /app/requirements.txt

# set working directory
WORKDIR /app

# install requirements
RUN pip install -U pip
RUN pip install -r requirements.txt

# make sure 'src' is in python path - this is so imports work
ENV PYTHONPATH=${PYTHONPATH}:/app/application
