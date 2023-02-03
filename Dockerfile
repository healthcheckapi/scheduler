
# using ubuntu LTS version
FROM ubuntu:20.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN mkdir healthcheck

RUN apt-get update 
RUN apt-get install -y cron
RUN apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# ADD crontab /etc/cron.d/cronjob
# RUN chmod 0644 /etc/cron.d/cronjob

# RUN apt-get install cron -y

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3.9 -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /healthcheck

WORKDIR /healthcheck
RUN touch /tmp/out.txt

EXPOSE 5000/tcp

# /dev/shm is mapped to shared memory and should be used for gunicorn heartbeat
# this will improve performance and avoid random freezes
# CMD ["python", "check_script/script.py", "d9bd2ce6-9aa2-4145-bcbb-4ba8aca489b9", "/healthcheck/check_script"]
CMD ["python", "api.py"]
