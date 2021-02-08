FROM continuumio/miniconda3:4.7.10-alpine
#############
# As `root` #
#############
USER root

ENV PATH=/opt/conda/bin:$PATH

COPY requirements.txt .
RUN conda create --name my && \
    . activate my && \
    conda install \
    --name my \
    --channel conda-forge \
    --channel dlr-sc \
    --channel tpaviot \
    --channel pythonocc \
    --channel oce \
    --file requirements.txt && \
    conda clean --all && \
    apk add \
    --no-cache \
    --virtual .pythonocc-core-runtime-dependencies \
    glu

ENV PATH=/opt/conda/envs/my/bin:$PATH

RUN apk add --no-cache \
    dumb-init

ENV HOME=/home/anaconda
RUN ln -s ${HOME}/app /app

#################
# As `anaconda` #
#################
USER anaconda
WORKDIR /app

RUN echo ". activate my" >> ~/.shinit
ENV ENV=${HOME}/.shinit

COPY --chown=anaconda:anaconda . .

EXPOSE 8000
# ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
