FROM debian:latest
# Debian Buster 10 (Server) install FinerPlan with uwsgi and nginx
# Reference: https://hackersandslackers.com/deploy-flask-uwsgi-nginx/

ARG USWGI_HOME=/etc/uwsgi
ARG FINERPLAN_HOME=/opt/finerplan
# 1. Prepare application directory and permissions
RUN useradd \
        --system --shell /usr/sbin/nologin \
        --no-create-home --home-dir $FINERPLAN_HOME \
        --uid 999 \
        finerplan && \
    mkdir $FINERPLAN_HOME && \
    chown finerplan:finerplan $FINERPLAN_HOME  && \
    chmod 755 $FINERPLAN_HOME  && \
    useradd \
        --system --shell /usr/sbin/nologin \
        --no-create-home --home-dir $USWGI_HOME \
        --uid 998 --groups finerplan \
        uwsgi

# 2. Install dependencies
RUN apt-get update && \
    apt-get install -y git python3-venv uwsgi nginx && \
    rm -rf /var/lib/apt/lists/*

# 3. Obtain FinerPlan
## Get package code and Prepare package environment
WORKDIR $FINERPLAN_HOME
RUN git clone https://github.com/fcqueiroz/finerplan.git . && \
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install -r requirements.txt && \
    deactivate && \
    rm -rf .git/ .github/ .gitignore setup.py .flaskenv && \
    chown -R finerplan:finerplan /opt/finerplan

# 4. Configure uWSGI
WORKDIR $USWGI_HOME
COPY finerplan.ini ./apps-available/finerplan.ini
RUN chown uwsgi:uwsgi ./apps-available/finerplan.ini && \
    chmod 744 ./apps-available/finerplan.ini && \
    ln -s $USWGI_HOME/apps-available/finerplan.ini ./apps-enabled/finerplan.ini && \
    echo "uwsgi --emperor /etc/uwsgi/app-enabled --daemonize /var/log/uwsgi-emperor.log" > /etc/rc.local

# 5. Configure Nginx
WORKDIR /etc/nginx
COPY finerplan.conf ./sites-available/finerplan.conf
RUN rm ./sites-enabled/default && \
    ln -s /etc/nginx/sites-available/finerplan.conf ./sites-enabled/finerplan.conf && \
    service nginx restart

WORKDIR /
EXPOSE 80

CMD ['uwsgi /opt/finerplan/finerplan.sock']

# 5. Set FINERPLAN_DATABASE and FINERPLAN_SECRET_KEY variables!!
# Reference: https://serverfault.com/questions/413397/how-to-set-environment-variable-in-systemd-service

## Steps in comments
