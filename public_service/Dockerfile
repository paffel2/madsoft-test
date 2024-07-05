FROM python:3.10.12

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libpq-dev libjpeg-dev

RUN useradd -rms /bin/bash server && chmod 777 /opt /run

WORKDIR /server

RUN chown -R server:server  /server && chmod 777 /server

COPY --chown=server:server . .

RUN pip install -r requirements.txt

USER server