# In the long term, having WM in its own container and Transmission in another would seem like an ideal approach.
# Unfortunately, it's hard to make that work with WM's management of Transmission instances, so, this is a stop-gap approach
FROM ubuntu:xenial

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

# We need sudo for the setup scripts, and Upstart for the transmission services
RUN apt-get update && apt-get -y install sudo upstart-sysv sysvinit-utils

RUN ./setup.sh
RUN ./setup_transmission-2.92.sh

# Seems like we can't rely on the DB being ready at this point, so cannot run manage.py migrate here.