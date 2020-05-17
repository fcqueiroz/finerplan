# FinerPlan Web Server
# Reference:
# - https://hackersandslackers.com/deploy-flask-uwsgi-nginx/
# - https://medium.com/bitcraft/docker-composing-a-python-3-flask-app-line-by-line-93b721105777
# - https://medium.com/@greut/minimal-python-deployment-on-docker-with-uwsgi-bc5aa89b3d35

FROM debian:bullseye-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y uwsgi uwsgi-plugin-python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies for app
COPY ./requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Configure timezone and locales
# Ref: https://serverfault.com/a/689947
RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/*
ARG lang_opt_1=pt_BR.UTF-8
ARG lang_opt_2=en_US.UTF-8
RUN echo "America/Sao_Paulo" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    sed -i -e "s/# $lang_opt_2 UTF-8/$lang_opt_2 UTF-8/" /etc/locale.gen && \
    sed -i -e "s/# $lang_opt_1 UTF-8/$lang_opt_1 UTF-8/" /etc/locale.gen && \
    echo "LANG='$lang_opt_1'">/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=$lang_opt_1
ENV LANG $lang_opt_1

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
