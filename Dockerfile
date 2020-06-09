# FinerPlan Web Server
# Reference:
# - https://hackersandslackers.com/deploy-flask-uwsgi-nginx/
# - https://medium.com/bitcraft/docker-composing-a-python-3-flask-app-line-by-line-93b721105777
# - https://medium.com/@greut/minimal-python-deployment-on-docker-with-uwsgi-bc5aa89b3d35

FROM debian:bullseye-20200514-slim

RUN apt-get update && \
    apt-get -qq install uwsgi uwsgi-plugin-python3 python3-pip locales && \
    apt-get purge -y gcc && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Configure timezone and locales
# Ref: https://serverfault.com/a/689947
ARG DEFAULT_LANG=pt_BR.UTF-8
RUN echo "America/Sao_Paulo" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    sed -i -e "s/# $DEFAULT_LANG/$DEFAULT_LANG/" /etc/locale.gen && \
    echo "LANG='$DEFAULT_LANG'">/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=$DEFAULT_LANG
ENV LANG $DEFAULT_LANG

ARG APP_FOLDER=/var/lib/finerplan
RUN mkdir -p $APP_FOLDER
WORKDIR $APP_FOLDER

ARG UWSGI_USER=uwsgi
RUN useradd -r -M -s /usr/sbin/nologin $UWSGI_USER && \
    chown -R $UWSGI_USER:$UWSGI_USER $APP_FOLDER
ENV UWSGI_USER $UWSGI_USER

ARG REQUIREMENTS_FILE=./requirements.txt
COPY $REQUIREMENTS_FILE /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

ARG FINERPLAN_PACKAGE
COPY ./dist/$FINERPLAN_PACKAGE /tmp/$FINERPLAN_PACKAGE
RUN pip3 install --no-cache-dir /tmp/$FINERPLAN_PACKAGE

ARG WSGI_ENTRYPOINT=./wsgi.py
COPY $WSGI_ENTRYPOINT $APP_FOLDER/wsgi.py
COPY ./scripts/start_finerplan $APP_FOLDER/start_finerplan

VOLUME $APP_FOLDER/app.db
VOLUME /etc/uwsgi/apps-enabled/finerplan.ini

ENV FINERPLAN_SECRET_KEY realfinerplan
ENV FINERPLAN_DATABASE $APP_FOLDER/app.db
ENV FINERPLAN_PORT 3031
EXPOSE $FINERPLAN_PORT

CMD ["./start_finerplan", "production"]

