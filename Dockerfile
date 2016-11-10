# In the long term, having WM in its own container and Transmission in another would seem like an ideal approach.
# Unfortunately, it's hard to make that work with WM's management of Transmission instances, so, this is a stop-gap approach
FROM ubuntu:trusty

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

# Prep for running the setup scripts without modifying them. Will run as root but still need sudo command to avoid errors
RUN apt-get update && apt-get -y install sudo

RUN ./setup.sh
RUN ./setup_transmission-2.92.sh

# Seems like we can't rely on the DB being ready at this point, so cannot run manage.py migrate here.