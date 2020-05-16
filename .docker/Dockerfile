FROM python:3.8-slim-buster
# Debian Buster 10 (Server) install FinerPlan with uwsgi and nginx
# Reference: https://hackersandslackers.com/deploy-flask-uwsgi-nginx/

RUN useradd finerplan
WORKDIR /home/finerplan
COPY ./requirements.txt ./requirements.txt
RUN which python
RUN pip3 install -r requirements.txt
USER finerplan

EXPOSE 5000

# 5. Set FINERPLAN_DATABASE and FINERPLAN_SECRET_KEY variables!!
# Reference: https://serverfault.com/questions/413397/how-to-set-environment-variable-in-systemd-service

## Steps in comments
