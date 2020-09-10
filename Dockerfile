# For use in mybinder.org Jupyter notebooks
# Eli (9/10/20): "slim" python docker images do not have gcc necessary to compile mantarray-waveform-analysis
FROM python:3.7.9-buster
# install the notebook package # Eli (9/10/20): no known reason for those specific versions of pip/notebook. Just pinning it for good practice
RUN pip install --no-cache --upgrade pip==20.2.3 && \
    pip install --no-cache notebook==6.1.4

# Eli (9/10/20): no known reason for this specific version of Cython (needed until we can get the .c files packaged in the mantarray-waveform-analysis sdist), just pinning it for good practice
RUN pip install Cython==0.29.21 --no-cache

RUN pip install curibio.sdk --no-cache --no-binary "mantarray-waveform-analysis"

# create user with a home directory
ARG NB_USER
ARG NB_UID
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}
USER ${USER}

