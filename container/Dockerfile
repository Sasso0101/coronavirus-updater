FROM ubuntu
RUN apt-get update && apt-get -y install nano cron python3-pip locales
WORKDIR /app
COPY app/ .

RUN pip3 install -r requirements.txt
RUN locale-gen it_IT.UTF-8
RUN update-locale

VOLUME /app

RUN echo "0,5,10,15,20,25,30,35,40,45,50,55 * * * * root /app/updater.sh > /proc/1/fd/1 2>/proc/1/fd/2" > /etc/crontab
# run crond as main process of container
CMD ["cron", "-f"]