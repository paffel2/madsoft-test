FROM python:3.10.12

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libpq-dev libjpeg-dev

RUN useradd -rms /bin/bash s3_server && chmod 777 /opt /run

WORKDIR /s3_server

RUN chown -R s3_server:s3_server  /s3_server && chmod 777 /s3_server

COPY --chown=s3_server:s3_server . .

RUN pip install -r requirements.txt

USER s3_server