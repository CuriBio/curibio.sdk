# For use in mybinder.org Jupyter notebooks
FROM python:3.7.9-slim-buster
# install the notebook package # Eli (9/10/20): no known reason for those specific versions of pip/notebook. Just pinning it for good practice
RUN pip install --no-cache --upgrade pip==20.2.3 && \
    pip install --no-cache notebook==6.1.4 && \
    pip install --no-cache jupyterlab==2.2.8

RUN pip install curibio.sdk --no-cache

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

# copy files from cloned repo into the HOME directory
COPY . ${HOME}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}
USER ${USER}

ENTRYPOINT []
