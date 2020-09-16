# For use in mybinder.org Jupyter notebooks
FROM python:3.8.5-slim-buster
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


RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# copy files from cloned repo into the HOME directory
# chown flag is necessary to make sure that the Notebooks don't launch as "read only" mode (without chown they are still owned by the 'root' user)
#COPY . ${HOME}
COPY --chown=${NB_USER}:${NB_USER} . ${HOME}/repo
# Eli (9/16/20): for some reason Docker is giving weird errors attempting to copy directly into
# COPY ./notebooks/ ${HOME} # to make it simpler for the users, just copy the notebooks folder right into the main Home directory. The URL links point to the file struction in the Home directory, so make sure to adjust those accordingly
# COPY ./tests/h5/v0.3.1/MA201110001__2020_09_03_213024/ ${HOME}/test-data

# COPY --chown=${NB_USER}:${NB_USER} ./notebooks/ ${HOME} # to make it simpler for the users, just copy the notebooks folder right into the main Home directory. The URL links point to the file struction in the Home directory, so make sure to adjust those accordingly
# COPY --chown=${NB_USER}:${NB_USER} ./tests/h5/v0.3.1/MA201110001__2020_09_03_213024/ ${HOME}/test-data

WORKDIR ${HOME}
USER ${USER}
# clear out the unneeded files copied from the repo
#RUN rm *
COPY ./repo/notebooks .
COPY ./repo/tests/h5/v0.3.1/MA201110001__2020_09_03_213024/ ./test-data
# clear out the folders