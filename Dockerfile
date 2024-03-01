# base image: python version 3.9 in a linux alpine 3.13 installation; the latter is a stripped down version of a linux installation, ideal for running docker containers as it doesnt
# have any unecessary dependencies. You can find different versions at: hub.docker.com and search for "python" as a base image. Then you see a list of image tags. So basically: "python" is
# the name of the docker image and "3.9-alpine3.13" is the name of the tag we'll use
FROM python:3.9-alpine3.13
# we define the maintainer (who will be maintaining this docker image)
LABEL maintainer="Nikos Leounakis"

# the below is recommended when running python in a docker container: it tells python that we don't want to buffer the output; the output from python will be printed directly to the console, which prevents
# any delays of msgs getting from our python running application  to the screen.
ENV PYTHONUNBUFFERED 1

# copy our requirements from our local txt file in our local machine to /tmp/requirements.txt, so basically copy the local requirements file into the docker image
COPY ./requirements.txt /tmp/requirements.txt

# copy requirements.dev.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# copy the app directory (the one that will later contain our django app) to /app inside the container
COPY ./app /app

# set the working directory from where commands will be run from when we run commands on our docker image. We are setting it to the location where our Django project is going to be synced to so that 
# when we run the commands we don't have to specify the full path of the django management command
WORKDIR /app

# we want to expose port 8000 from our container to our machine when we run the container. So this allows us to access that port on the cotnainer that is running from our image. This way we can 
# connect to the Django developnment server.
EXPOSE 8000


#check requirements.dev.txt: this is overwritten by the line in the docker-compose: ARG DEV=true
ARG DEV=false

# this RUN command runs a command on the alpine image. It will install some dependencies on our machine
# You could use a RUN for each line in the block below but this would create a new image layer for each RUN we run; but we want to keep our images as lightweight
# as possible.

# the first line creates a new venv inside the docker image to install our dependencies. For most of the time, you dont need to work with venvs when working 
# with Docker, but there are some cases where there are some python dependencies on the base image that might conflict with the python dependencies for 
# your project.

# then we upgrade pip for the virtual enviroment we created by specifying the full path to our virtual environment (/py/bin/).
# then we install our requirements inside the docker image inside the virtual environment
# then we remove the /tmp directory; we dont want any extra dependencies on our image, it's best practice to keep docker images lightweight and remove any files 
# you dont need during building the image -> more speed and less space when deploying the application

# then we add a new user inside our image in order not to use the root user. if we didnt do this, the only user inside the alpine image would be the root user;
# this is the user that has the full accessing permisisons to do everything on the server. it's not recommended to run the application using the root user bc if
# the application gets compromised, then the attacker may have full access to everything on that docker container. Whereas by specifying a user like we do here, 
# the attacker will only be able to do what this limited user can do.
# Finally we specify the name of the user, you can call it whatever you want.
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \ 
    /py/bin/pip install -r /tmp/requirements.txt && \
    #check requirements.dev.txt
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Here we update the path environment variable inside the image. The path is the environment variable that is automatically created in Linux systems and it
# defines all the directories where executables can be run. So when we run a command in our project, we dont want to specify the full path of our virtual
# environment.
ENV PATH="/py/bin:$PATH"

# This is the usual final line of a dockerfile. It specifies the user we are switching to. Up to this line, everything is done by the root user and the containers
# that are made out of this image will be run using the last user that the image switched to.
USER django-user