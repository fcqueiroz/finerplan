# FinerPlan Web Server
# Reference:
# - https://hackersandslackers.com/deploy-flask-uwsgi-nginx/
# - https://medium.com/bitcraft/docker-composing-a-python-3-flask-app-line-by-line-93b721105777
# - https://medium.com/@greut/minimal-python-deployment-on-docker-with-uwsgi-bc5aa89b3d35
# TODO: In a regular image, locales use 31MB and manual pages another 5MB
# We can possibly reduce 35MB in image size by compiling our own image

FROM debian:bullseye-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y uwsgi uwsgi-plugin-python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies for app
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set the directory where we'll be running the app
ENV APP_FOLDER /usr/src/app
RUN mkdir -p $APP_FOLDER
WORKDIR $APP_FOLDER

# Create unprivileged user for running the web server
ENV UWSGI_USER uwsgi
RUN useradd -r -M -s /usr/sbin/nologin $UWSGI_USER && \
    chown -R $UWSGI_USER:$UWSGI_USER $APP_FOLDER

# Define volume containing the uwsgi configuration
VOLUME $APP_FOLDER/uwsgi.ini

# Define volume containing the source code
VOLUME $APP_FOLDER/finerplan
# Copy uwsgi app entrypoint
COPY ./wsgi.py $APP_FOLDER/wsgi.py

# Set the port uWSGI will listen on
ENV UWSGI_PORT 3031
EXPOSE $UWSGI_PORT

# Set FinerPlan environment variables
ENV FINERPLAN_SECRET_KEY realfinerplan
ENV FINERPLAN_DATABASE $APP_FOLDER/finerplan.db
VOLUME $APP_FOLDER/finerplan.db

# Set uwsgi with proper configuration as the default command to run
CMD ["uwsgi", "uwsgi.ini"]



## Steps in comments
