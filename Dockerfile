# FinerPlan Web Server
# Reference:
# - https://hackersandslackers.com/deploy-flask-uwsgi-nginx/
# - https://medium.com/bitcraft/docker-composing-a-python-3-flask-app-line-by-line-93b721105777
# - https://medium.com/@greut/minimal-python-deployment-on-docker-with-uwsgi-bc5aa89b3d35
FROM python:3.7-slim-buster

# Install Python dependencies fpr app
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Set the directory where we'll be running the app
ENV APP /usr/src/app

RUN mkdir -p $APP
WORKDIR $APP

# Create unprivileged user for running the web server
RUN useradd -r -M -s /usr/sbin/nologin uwsgi && \
    chown -R uwsgi:uwsgi $APP
# Install uwsgi and python3 plugins
RUN apt-get update && \
    apt-get install -y uwsgi uwsgi-src uwsgi-plugin-python3 && \
    rm -rf /var/lib/apt/lists/*
# Install uWSGI python38 plugin
#RUN export PYTHON=python3.8 && \
#    uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python38" && \
#    mv python38_plugin.so /usr/lib/uwsgi/plugins/ && \
#    chmod 666 /usr/lib/uwsgi/plugin/python38_plugin.so

# Define volume containing the uwsgi configuration
VOLUME $APP/uwsgi.ini

# Define volume containing the source code
VOLUME $APP/finerplan
# Copy uwsgi app entrypoint
COPY ./wsgi.py $APP/wsgi.py

# Set the port uWSGI will listen on
ENV PORT 3031
EXPOSE $PORT

# Set FinerPlan environment variables
ENV FINERPLAN_DATABASE $APP/finerplan.db
ENV FINERPLAN_SECRET_KEY realfinerplan


# Set uwsgi with proper configuration as the default command to run
CMD ["uwsgi", "$APP/uwsgi.ini"]



## Steps in comments
