FROM python:3.11-slim-buster

# Setting the working directory in docker image
WORKDIR /code

# Creating user and directories
RUN useradd appuser && \
    chown -R appuser /code

# Copying only the necessary files
COPY ./requirements.txt /code/requirements.txt

# Installing dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Setting the environment variables
ARG API_URL
ENV API_URL=$API_URL
ENV PORT=8501

# Copy necessary files
COPY ./home.py /code/home.py

# Switching to our app user
USER appuser

# Running the application
CMD streamlit run home.py --server.port $PORT