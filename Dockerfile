FROM python:3.5
ENV PYTHONUNBUFFERED 1

#MAINTAINER Andreas Backx

RUN mkdir /code
WORKDIR /code

# uWSGI
# apt-get update and install on same line to prevent caching issues
RUN apt-get update && apt-get install -y \
    libpcre3 \
    libpcre3-dev \
&& rm -rf /var/lib/apt/lists/* \
RUN pip install uwsgi

# Arguments
ARG version
ARG certificate_type
ARG requirements_file=requirements.txt
ARG db_name=LB_${version}
ARG db_user=LB_${version}
ARG STATIC_ROOT='/var/lunchbreak/static'
ARG MEDIA_ROOT='/var/lunchbreak/media'
ARG MEDIA_PRIVATE_ROOT='/var/lunchbreak/media-private'

# Environment
ENV DB_NAME ${db_name}
ENV DB_USER ${db_user}
ENV certificates_path "/etc/lunchbreak/certificates/apns"
ENV BUSINESS_APNS_CERTIFICATE "${certificates_path}/business_${certificate_type}.pem"
ENV CUSTOMERS_APNS_CERTIFICATE "${certificates_path}/customers_${certificate_type}.pem"
ENV DJANGO_SETTINGS_VERSION ${version}
ENV MEDIA_ROOT ${MEDIA_ROOT}
ENV PRIVATE_MEDIA_ROOT ${PRIVATE_MEDIA_ROOT}

# Setting up entrypoint
COPY ./docker/lunchbreak/docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Code
COPY ./lunchbreak/${requirements_file} /code/${requirements_file}
RUN pip install -r ${requirements_file} --exists-action w

COPY ./lunchbreak /code/
